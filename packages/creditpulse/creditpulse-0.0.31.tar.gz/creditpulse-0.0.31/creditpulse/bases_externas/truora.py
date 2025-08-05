"""
    Request manager ara base de datos externa truora
"""
import json
import os
import logging
from typing import Optional, Union

import requests
from creditpulse.requests.request_manager import RequestManager
from creditpulse.bases_externas.schema import (
    TruoraCheckData,
    CountryCode, PersonType,
    CheckStatus,
    GeneralDatabase,
    BasesDeDatos,
    TruoraCustomSchema,
    parse_json_to_model,
    CreditScoreData,
    PersonalDetails,
    parse_check_to_score,
    Scores,
    PersonaJuridica,
    PersonaNatural
)
from creditpulse.common.error_messages import (
    AutorizacionDatosPersonales,
    TruoraApiKeyRequired,
    TruoraGeneralError
)

from creditpulse.bases_externas.database import Database

# https:www.postman.com/truora-api-docs/truora-api-docs/collection/iwmyaus/truora-collection
TRUORA_API_VERSIONS = '/v1'
TRUORA_HOST = 'https://checks.truora.com'
# TRUORA_HOST = ' http://127.0.0.1:8000'

TRUORA_API_URL = TRUORA_HOST + '/checks-api'

TRUORA_BASE_URL = TRUORA_API_URL + TRUORA_API_VERSIONS
CHECK_URL = TRUORA_BASE_URL + '/checks'
CHECK_URL_DETAILS = TRUORA_BASE_URL + '/checks/{}/details'
CHECK_URL_SUMMARIZE = TRUORA_BASE_URL + '/checks/{}/summarize'
CHECK_SETTINGS_URL = ' https://api.checks.truora.com/v1/settings'
CUSTOM_CHECK_URL = TRUORA_BASE_URL + '/config'

settings_data = {
    'names_matching_type': 'exact',
    'retries': True,
    'max_duration': '3m'
}


class TruoraCustomConfig:

    def __init__(self, session: requests.Session, model: TruoraCustomSchema):
        self.session = session
        self.model = model
        self.client_id = None
        self.config_id = None
        self.deleted = False

    def create(self):
        """
        Store custom type in truora
        :return:
        """
        response = self.session.post(CHECK_URL, data=self.model.model_dump_json()).json()
        self.client_id = response.get('client_id', None)
        self.config_id = response.get('config_id', None)
        return response

    def delete(self):
        """
        Delete from truora the self content type
        :return:
        """
        params = {
            'type': self.model.type,
            'country': self.model.country,
        }
        self.deleted = True
        return self.session.delete(CHECK_URL, params=params)

    def update(self, new_model: TruoraCustomSchema):
        self.model = new_model.model_copy(update={"type": self.model.type, "country": self.model.country})
        return self.session.put(CHECK_URL, data=self.model.model_dump_json())


class Truora(Database):
    """

    Clase principal para consultar base de datos externa truora
    """

    def get_name(self) -> BasesDeDatos:
        return BasesDeDatos.TRUORA

    def _get_check(self, check_id: str):
        return self.session.get(CHECK_URL + "/" + check_id)

    def on_execute(self) -> requests.Response:
        return self._get_check(self.tcheck.check.check_id)

    def success_callback(self, response: requests.Response) -> None:
        self.logger.info("Consulta a Base De datos ha sido finalizada")
        response_json = response.json()
        self.tcheck = TruoraCheckData(**response_json)
        self.status = self.tcheck.check.status

    def error_callback(self, response: requests.Response) -> None:
        response_json = response.json()
        inter_check: TruoraCheckData = TruoraCheckData(**response_json)

        if inter_check.check.status == CheckStatus.DELAYED:
            self.request_manager.update_backoff_factor(self.request_manager.backoff_factor + 0.5)
            self.logger.warning("Consulta base de datos ha sido delayed")

        self.status = inter_check.check.status

    def is_request_successful(self, response: requests.Response) -> bool:
        """

        :param response:
        :return:
        """
        if response.status_code in [200, 203]:
            response_json = response.json()
            try:
                t_checker: TruoraCheckData = TruoraCheckData(**response_json)
                return t_checker.check.status == CheckStatus.COMPLETED
            except:
                return False
        return False

    def __init__(self, logger: logging.Logger = None):
        """
        Create a new instance of truora dataabase
        :param logger:
        """
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

        self.api_key = os.environ.get('TRUORA_API_TOKEN')

        if self.api_key is None:
            e = TruoraApiKeyRequired()
            self.logger.error(e)
            raise e

        self.session = requests.session()

        self.session.headers.update({
            "Truora-API-Key": self.api_key,
            'Accept': 'application/json'
        })

        self.request_manager = RequestManager(
            manager=self,
            max_retries=30
        )

        self.tcheck: Optional[TruoraCheckData] = None

        self.logger = logging.getLogger(__name__)

        self.status: CheckStatus = CheckStatus.NOT_STARTED

    def create_check(self,
                     identificacion: str,
                     person_type: Union[PersonType, str],
                     autorizacion_datos: bool = False,
                     pais: CountryCode = CountryCode.COLOMBIA
                     ) -> str:
        """
        Funcion principal para consulatr base de datos externa tuora

        :param identificacion:
        :param person_type:
        :param autorizacion_datos:
        :param pais:
        :return:
        """
        if not autorizacion_datos:
            raise AutorizacionDatosPersonales()

        settings_response = self.session.post(CHECK_SETTINGS_URL, data=settings_data)
        response_json = settings_response.json()

        if settings_response.status_code not in [200, 201, 202, 203]:
            self.logger.error(f"Error al crear consulta base de datos externa: {response_json['message']}")
            raise TruoraGeneralError(f"Error al crear consulta base de datos externa: {response_json['message']}")

        form_data = {
            'national_id': identificacion,
            'country': pais,
            'type': person_type,
            'user_authorized': autorizacion_datos,
            'force_creation': True
        }
        try:
            response = self.session.post(CHECK_URL, data=form_data)
            response_json = response.json()

            if response.status_code not in [200, 201, 202, 203]:
                self.logger.error(f"Error al crear consulta base de datos externa: {response_json['message']}")
                raise TruoraGeneralError(f"Error al crear consulta base de datos externa: {response_json['message']}")

            self.tcheck = TruoraCheckData(**response_json)

            if self.tcheck is None:
                raise TruoraGeneralError('Check de truora no fue creado')

            self.request_manager.start()

            return self.tcheck.check.check_id
        except Exception as e:
            self.logger.error(e)

    def get_check(self, check_id: str):
        """

        :param check_id:
        :return:
        """
        response = self._get_check(check_id=check_id)
        if response.status_code not in range(200, 203):
            self.logger.error(response.text)
            raise TruoraGeneralError(response.text)

        return json.loads(response.text)

    def get_check_summary(self, check_id: str):
        """

        :param check_id:
        :return:
        """
        response = self.session.get(CHECK_URL_SUMMARIZE.format(check_id))
        if response.status_code not in range(200, 203):
            self.logger.error(response.text)
            raise TruoraGeneralError(response.text)

        return json.loads(response.text)

    def get_check_details(self, check_id: str):
        """

        :param check_id:
        :return:
        """
        response = self.session.get(CHECK_URL_DETAILS.format(check_id))
        if response.status_code not in range(200, 203):
            self.logger.error(response.text)
            raise TruoraGeneralError(response.text)

        return json.loads(response.text)

    def get_next_details(self, next_url: str):
        """

        :param check_id:
        :return:
        """
        response = self.session.get("{}/{}".format(TRUORA_API_URL, next_url))
        if response.status_code not in range(200, 203):
            self.logger.error(response.text)
            raise TruoraGeneralError(response.text)

        return json.loads(response.text)

    def to_general(self, check_id: str) -> GeneralDatabase:
        """
        Traduce truora a general
        :return:
        """
        check_data = self.get_check(check_id=check_id)
        scores = parse_check_to_score(json_data=check_data, model_class=Scores)

        details = self.get_check_details(check_id=check_id)
        credit_data = parse_json_to_model(json_data=details, model_class=CreditScoreData)

        personal_details = PersonalDetails()

        next = details.get('next')

        juridica = parse_json_to_model(json_data=details, model_class=PersonaJuridica)

        natural = parse_json_to_model(json_data=details, model_class=PersonaNatural)

        if next or not isinstance(next, str):
            next_details = self.get_next_details(next_url=details.get('next'))
            personal_details = parse_json_to_model(json_data=next_details, model_class=PersonalDetails)

        return GeneralDatabase(
            check_id=check_id,
            credit_data=credit_data,
            personal_data=personal_details,
            scores=scores,
            juridica=juridica,
            natural=natural
        )

    def create_custom_type(self, model: TruoraCustomSchema) -> TruoraCustomConfig:
        """
        Create a custom type on truora database
        :return:
        """
        custom_type = TruoraCustomConfig(session=self.session, model=model)
        custom_type.create()
        return custom_type

    def list_custom_type(self):
        response = self.session.get(CUSTOM_CHECK_URL)
        if response.status_code not in range(200, 203):
            self.logger.error(response.text)
            raise TruoraGeneralError(response.text)

        return json.loads(response.text)
