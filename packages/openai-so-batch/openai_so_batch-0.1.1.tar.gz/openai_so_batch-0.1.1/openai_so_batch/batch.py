from pathlib import Path
import json

from openai import OpenAI


class Batch:
    def __init__(
        self,
        input_file,
        output_file,
        error_file,
        job_name,
        batch_id=None
    ):
        """
        Initialize a batch object.

        Args:
            input_file: The path to the input file.
            output_file: The path to the output file.
            error_file: The path to the error file.
            job_name: The name of the job.
            batch_id (optional): The ID of the batch. If provided, the input_file is ignored and the batch is retrieved from the API.
        """
        self.client = OpenAI()

        if (input_file is not None) and (batch_id is not None):
            raise ValueError("Only one of batch_id or input_file must be provided")

        self.input_file = input_file
        self.output_file = output_file
        self.error_file = error_file
        self.job_name = job_name
        self.batch_id = batch_id

    def add_task(
        self,
        id,
        model,
        system_prompt,
        user_prompt,
        response_model
    ):
        schema = response_model.model_json_schema()
        schema["additionalProperties"] = False

        task = {
            "custom_id": f"id-{id}",
            "method": "POST",
            "url": "/v1/responses",
            "body": {
                "model": model,
                "input": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_prompt},
                ],
                "text": {
                    "format": {
                        "type":   "json_schema",
                        "name":   response_model.__name__,
                        "strict": True,
                        "schema": schema
                    }
                }
            }
        }

        with open(self.input_file, "a") as f:
            f.write(json.dumps(task) + "\n")

    def _validate_input_file(self):
        if not Path(self.input_file).exists():
            raise FileNotFoundError(f"Input file {self.input_file} does not exist")

        if not Path(self.input_file).is_file():
            raise ValueError(f"Input file {self.input_file} is not a file")

        ids = []
        with open(self.input_file, "r") as f:
            for line in f.readlines():
                data = json.loads(line)

                if data['custom_id'] in ids:
                    raise ValueError(f"Custom ID {data['custom_id']} is not unique")

                ids.append(data['custom_id'])

    def upload(self):
        self._validate_input_file()

        file_id = self.client.files.create(
            file=open(self.input_file, "rb"),
            purpose="batch"
        ).id

        batch = self.client.batches.create(
            input_file_id     = file_id,
            endpoint          = "/v1/responses",
            completion_window = "24h",
            metadata          = {"job": self.job_name}
        )

        self.batch_id = batch.id

    def get_status(self):
        batch = self.client.batches.retrieve(self.batch_id)
        return batch.status

    def download(self):
        batch = self.client.batches.retrieve(self.batch_id)

        if batch.output_file_id:
            contents = self.client.files.content(batch.output_file_id).content
            Path(self.output_file).write_bytes(contents)

        if batch.error_file_id:
            contents = self.client.files.content(batch.error_file_id).content
            Path(self.error_file).write_bytes(contents)

        return self.client.batches.retrieve(self.batch_id).status
