"""
    Clase abstracta para definir una base de datos
"""
from typing import Union

from creditpulse.bases_externas.schema import PersonType, CountryCode, GeneralDatabase, BasesDeDatos, \
    TruoraCustomSchema, TruoraCheckData
from creditpulse.requests.request_manager import RequestActionManager
from abc import ABC, abstractmethod


class Database(RequestActionManager, ABC):


    @abstractmethod
    def create_check(self, identificacion: str,
                     person_type: Union[PersonType, str],
                     autorizacion_datos: bool = False,
                     pais: CountryCode = CountryCode.COLOMBIA
                     ) -> str:
        """
        Implementacion de
        :param identificacion:
        :param person_type:
        :param autorizacion_datos:
        :param pais:
        :return:
        """

    @abstractmethod
    def get_name(self) -> BasesDeDatos:
        """
        Da el nombre de la actual base de datos
        :return:
        """

    @abstractmethod
    def to_general(self, check_id: str) -> GeneralDatabase:
        """
        Traduce base de datos a general
        :return:
        """

    @abstractmethod
    def get_check(self, check_id: str):
        """
        Retorna informacion general del check
        :return:
        """

    @abstractmethod
    def get_check_summary(self, check_id: str):
        """
        retorna informacion resumida del check
        :param check_id:
        :return:
        """

    @abstractmethod
    def get_check_details(self, check_id: str):
        """
        Retorna toda la informacion existente del check
        :param check_id:
        :return:
        """

    @abstractmethod
    def create_custom_type(self, model: TruoraCustomSchema):
        """

        :param model:
        :return:
        """

    @abstractmethod
    def list_custom_type(self):
        """
        Retorna lista de los custom tyopes
        :return:
        """
