# Copyright 2025 Zhejiang University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND.

import requests
import pandas as pd
from .response_body import ResponseBody
import os

class GeoCalciteClient:
    def __init__(self, token: str = "", base_url: str = "", timeout: int = 30):
        """
        :param token: Authorization token for the API, defaults to environment variable "Authorization"
        :param base_url: API root URL, e.g., "http://localhost:8088"
        :param timeout: HTTP request timeout in seconds
        """
        self.base_url = base_url if base_url!="" else os.getenv("GC_BASE_URL", "http://8.218.39.233:8088")
        self.timeout = timeout
        self.token = token if token != "" else os.getenv("AUTHORIZATION")
        self.headers = {"Authorization": self.token}
        self.session = requests.Session()

    def __post(self, endpoint: str, json_body: dict) -> ResponseBody:
        """
        Helper method to perform a POST request to the GeoCalcite API.
        :param endpoint: API endpoint to call
        :param json_body: JSON body to send in the request
        :return: JSON response from the API
        """

        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, json=json_body, timeout=self.timeout, headers=self.headers)
        try:
            response_body = ResponseBody.from_json(response.json())
        except ValueError:
            raise ValueError(f"Invalid JSON response: {response.text}")
        
        if response.status_code != 200 or response_body.code != 200:
            message = response_body.message or response.text
            raise requests.RequestException(f"[{response.status_code}] {message}")

        return response_body

    def connect(self, dids: list[int]) -> ResponseBody:
        """
        Connect to one or more data sources using their data identifiers (DIDs).
        :param dids: List of data identifiers to connect
        :return: ResponseBody object containing the response from the API
        """

        print(f"Attempting to connect to DIDs: {dids}")

        try:
            response_body = self.__post("/api/datahub/sql/connect", {"dids": dids})

            if response_body.code != 200:
                raise requests.RequestException(f"Failed to connect to DIDs: {response_body.message}")
            
            print(f"{response_body.message}")
            print(f"Data source tables: {response_body.data}")

            return response_body
        except Exception as e:
            print(f"Error connecting to DIDs: {e}")
            raise

    def refresh(self, dids: list[int]) -> ResponseBody:
        """
        Refresh the connection to one or more data sources using their data identifiers (DIDs).
        :param dids: List of data identifiers to refresh
        :return: ResponseBody object containing the response from the API
        """

        print(f"Attempting to refresh DIDs: {dids}")

        try:
            response_body = self.__post("/api/datahub/sql/refresh", {"dids": dids})

            if response_body.code != 200:
                raise requests.RequestException(f"Failed to refresh DIDs: {response_body.message}")
            
            print(f"{response_body.message}")
            print(f"Data source tables: {response_body.data}")

            return response_body
        except Exception as e:
            print(f"Error refreshing DIDs: {e}")
            raise

    def disconnect(self, dids: list[int]) -> ResponseBody:
        """
        Disconnect from one or more data sources using their data identifiers (DIDs).
        :param dids: List of data identifiers to disconnect
        :return: ResponseBody object containing the response from the API
        """

        print(f"Attempting to disconnect from DIDs: {dids}")

        try:
            response_body = self.__post("/api/datahub/sql/disconnect", {"dids": dids})

            if response_body.code != 200:
                raise requests.RequestException(f"Failed to disconnect from DIDs: {response_body.message}")
            
            print(f"{response_body.message}")
            print(f"Disconnect tables: {response_body.data}")

            return response_body
        except Exception as e:
            print(f"Error disconnecting from DIDs: {e}")
            raise

    def query(self, sql: str) -> pd.DataFrame:
        """
        Execute a SQL query against the connected data sources.
        :param sql: SQL query to execute
        :return: DataFrame containing the results of the query
        """

        print(f"Executing SQL query: {sql}")

        try:
            response_body = self.__post("/api/datahub/sql/query", {"sql": sql})

            if response_body.code != 200:
                raise requests.RequestException(f"Failed to execute SQL query: {response_body.message}")
            
            print(f"{response_body.message}")

            return pd.DataFrame(response_body.data)
        except Exception as e:
            print(f"Error executing SQL query: {e}")
            raise