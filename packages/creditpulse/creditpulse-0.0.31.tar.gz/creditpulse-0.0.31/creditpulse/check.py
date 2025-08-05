"""
Clase pincipal para analysis de creditos financieros

"""
import logging
import json
from typing import Union
from pathlib import Path

from creditpulse.bases_externas.schema import CountryCode, BasesDeDatos, PersonType
from creditpulse.bases_externas.truora import Truora, TruoraCustomSchema
from creditpulse.bases_externas.database import Database
from creditpulse.common.error_messages import AutorizacionNoOtorgada


class Check:
    """
        Clase que provee interfaz para analysis the personas
    """

    def __init__(self, database: BasesDeDatos = BasesDeDatos.TRUORA):
        # Module logger

        log_file = Path('logs/credit_pulse.log')
        log_file.parent.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            filename=log_file
        )
        self.logger = logging.getLogger(__name__)

        self.external: Database = Truora(logger=self.logger)
        # TODO implementar otras bases de datos

    def create_check(self, identificacion: str, autorizacion: bool,
                     check_type: Union[PersonType, str] = PersonType.COMPANIA):
        """
        Crea un check general en truora
        :return: Analysis financiero de la persona natural o juridica
        """
        if not autorizacion:
            raise AutorizacionNoOtorgada()

        return self.external.create_check(
            identificacion=identificacion,
            person_type=check_type,
            autorizacion_datos=autorizacion,
            pais=CountryCode.COLOMBIA
        )

    def get_existing_check(self, check_id: str):
        """
        Retorna
        :param check_id:
        :return:
        """
        return self.external.get_check(check_id=check_id)

    def get_existing_check_details(self, check_id: str):
        """

        :param check_id:
        :return:
        """
        return self.external.get_check_details(check_id=check_id)

    def get_existing_check_summary(self, check_id: str):
        """

        :param check_id:
        :return:
        """
        return self.external.get_check_summary(check_id=check_id)

    def create_custom_type(self, model: TruoraCustomSchema):
        """
        Crea un custom type en truora
        :param model:
        :return:
        """
        return self.external.create_custom_type(model=model)

    def to_general(self, check_id: str):
        """
        Create standard output for a check
        :param check_id:
        :return:
        """

        return self.external.to_general(check_id=check_id)

    def get_custom_types(self):
        return self.external.list_custom_type()