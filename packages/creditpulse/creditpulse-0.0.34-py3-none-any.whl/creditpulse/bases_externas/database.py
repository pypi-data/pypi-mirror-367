"""
    Clase abstracta para definir una base de datos
"""
import logging
import requests
from typing import Union
from pydantic import BaseModel
from abc import ABC, abstractmethod

from creditpulse.requests.request_manager import RequestActionManager
from creditpulse.bases_externas.schema import PersonType, CountryCode, GeneralDatabase, BasesDeDatos


class DatabaseConfiguration:
    session: requests.Session
    database_url: str
    base_model_class: BaseModel
    logger = logging.getLogger(__name__)

    def __init__(self, session: requests.Session):
        self.session = session

    @abstractmethod
    def list_configuration(self):
        """
        Return all configuration from database
        :return:
        """

    @abstractmethod
    def update_configuration(self, model: BaseModel):
        """
        Update the given configuration
        :param model:
        :return:
        """

    @abstractmethod
    def create_configuration(self, model: BaseModel):
        """
        Create the given configuration model
        :param model:
        :return:
        """

    @abstractmethod
    def delete_configuration(self, model: BaseModel):
        """
        Delete the given configuration
        :param model:
        :return:
        """

    @abstractmethod
    def create_default_configuration(self):
        """
        Create the default configuration on the database
        :param model:
        :return:
        """

    @abstractmethod
    def reset_default_configuration(self):
        """
        Reset the default configuration
        :return:
        """


class Database(RequestActionManager, ABC):
    configuration: DatabaseConfiguration

    @abstractmethod
    def create_check(self, identificacion: str,
                     person_type: Union[PersonType, str],
                     autorizacion_datos: bool = False,
                     pais: CountryCode = CountryCode.COLOMBIA,
                     check_name: str = 'default'
                     ) -> str:
        """
        Implementacion de
        :param check_name:
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
