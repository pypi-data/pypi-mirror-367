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

class ResponseBody:
    def __init__(self, code, message, data):
        """
        Initialize the ResponseBody instance.
        :param code: Response code (integer)
        :param message: Response message (string)
        :param data: Response data (can be of any type)
        """

        self.code = code
        self.message = message
        self.data = data

    @classmethod
    def from_json(cls, json: dict):
        """
        Create a ResponseBody instance from a JSON response.
        :param json: JSON response as a dictionary
        :return: ResponseBody instance
        """
        
        return cls(
            code=json.get("code"),
            message=json.get("message"),
            data=json.get("data")
        )