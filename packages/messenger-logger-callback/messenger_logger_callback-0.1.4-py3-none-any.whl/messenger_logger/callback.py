import requests
import json
import os
import datetime
import dataclasses
import dotenv
from transformers import TrainerCallback, TrainingArguments, TrainerState, TrainerControl
from typing import Dict, Any, Optional

class MessengerLoggerCallback(TrainerCallback):
    """
    A custom Hugging Face Trainer Callback to send training logs and custom data to a remote server.

    This callback intercepts logging events from the Trainer and sends the
    relevant metrics (loss, learning rate, epoch, etc.) as a JSON payload
    to a specified HTTP endpoint. It also provides a method to send custom,
    arbitrary data.

    Configuration can be provided through direct arguments, environment variables,
    or a .env file.

    Args:
        server_url (str, optional): The URL of the server endpoint where logs should be sent.
                                    If not provided, it will attempt to read from
                                    the MESSENGER_LOGGER_SERVER_URL environment variable.
                                    Example: "http://your-server.com/api/logs"
        project_name (str, optional): An identifier for the training project.
                                      Defaults to "default_project".
        run_id (str, optional): A unique identifier for the current training run.
                                If not provided, a unique ID will be generated
                                based on the current timestamp.
        auth_token (str, optional): An authentication token to include in the request headers.
                                    If not provided, it will attempt to read from
                                    the MESSENGER_LOGGER_AUTH_TOKEN environment variable.
        author_username (str, optional): The username of the author who initiated the run.
                                         Defaults to "anonymous" if not provided. This
                                         can be read from the MESSENGER_LOGGER_AUTHOR_USERNAME
                                         environment variable.
        metadata (Dict[str, Any], optional): A dictionary of static metadata to include with every log.
                                             This can be passed directly or as a JSON string
                                             in the MESSENGER_LOGGER_METADATA environment variable.
        dotenv_path (str, optional): Path to a .env file to load environment variables from.
                                     Defaults to None. This
                                     can be read from the MESSENGER_LOGGER_DOTENV
                                     environment variable.
    """
    def __init__(self, server_url: Optional[str] = None, project_name: str = "default_project",
                 run_id: Optional[str] = None, auth_token: Optional[str] = None,
                 author_username: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None,
                 dotenv_path: Optional[str] = None):

        # Load environment variables from the specified .env file if a path is provided.
        self.dotenv_path = dotenv_path if dotenv_path else os.getenv("MESSENGER_LOGGER_DOTENV")
        if self.dotenv_path:
            try:
                dotenv.load_dotenv(dotenv_path=self.dotenv_path)
                print(f"Loaded environment variables from {self.dotenv_path}")
            except Exception as e:
                print(f"Warning: Could not load .env file from {self.dotenv_path}. Error: {e}")

        # Determine server_url: Prioritize direct argument, then env variable.
        self.server_url = server_url if server_url else os.getenv("MESSENGER_LOGGER_SERVER_URL")
        if not self.server_url:
            raise ValueError(
                "server_url must be provided either as an argument, via an environment "
                "variable, or within a loaded .env file."
            )

        # Determine auth_token: Prioritize direct argument, then env variable.
        self.auth_token = auth_token if auth_token else os.getenv("MESSENGER_LOGGER_AUTH_TOKEN")
        if self.auth_token:
            print("Authentication token will be used for server requests.")

        # Determine author_username: Prioritize direct argument, then env variable, otherwise default.
        self.author_username = author_username if author_username else os.getenv("MESSENGER_LOGGER_AUTHOR_USERNAME", "anonymous")

        # Determine metadata: Prioritize direct argument, then parsed JSON from env variable.
        self.metadata = metadata or {}
        env_metadata_str = os.getenv("MESSENGER_LOGGER_METADATA")
        if env_metadata_str:
            try:
                env_metadata = json.loads(env_metadata_str)
                # Merge with any existing metadata from direct arguments
                self.metadata.update(env_metadata)
                print("Loaded metadata from environment variable.")
            except json.JSONDecodeError as e:
                print(f"Error: Could not parse MESSENGER_LOGGER_METADATA environment variable as JSON. Error: {e}")
            except Exception as e:
                print(f"An unexpected error occurred while processing metadata from env variable: {e}")


        self.project_name = project_name
        # Simple unique ID based on timestamp if not provided
        self.run_id = run_id if run_id else f"run_{int(datetime.datetime.now().timestamp())}"
        print(f"MessengerLoggerCallback initialized for project '{self.project_name}', run '{self.run_id}' by '{self.author_username}'")
        print(f"Logs will be sent to: {self.server_url}")
        if self.metadata:
            print(f"Including static metadata: {self.metadata}")

    def _get_trainer_state_info(self, state: TrainerState) -> Dict[str, Any]:
        """
        Extracts all attributes from TrainerState into a dictionary using dataclasses.asdict.
        This handles serialization of basic types and nested dataclasses automatically.
        """
        _state = dataclasses.asdict(state)
        log_history = _state.get("log_history", [])
        _state["log_history"] = log_history[:5]
        return _state

    def _send_payload(self, payload: Dict[str, Any], step: Optional[int] = None):
        """Helper method to send a JSON payload to the server with error handling."""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        final_payload = {
            "author_username": self.author_username,
            **self.metadata,
            **payload,
        }

        try:
            response = requests.post(self.server_url, json=final_payload, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            print(f"Warning: Request to {self.server_url} timed out for step {step if step is not None else 'N/A'}. "
                  "The server did not respond within the expected time.")
        except requests.exceptions.ConnectionError as e:
            print(f"Error: Could not connect to server at {self.server_url} for step {step if step is not None else 'N/A'}. "
                  f"The server might be unavailable or the URL is incorrect. Error details: {e}")
        except requests.exceptions.HTTPError as e:
            print(f"Error: HTTP error occurred while sending logs for step {step if step is not None else 'N/A'}. "
                  f"Status: {e.response.status_code}, Response: {e.response.text}. Check server logs for more details.")
        except Exception as e:
            print(f"An unexpected error occurred while sending logs for step {step if step is not None else 'N/A'}: {e}")

    def on_log(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, logs: Dict[str, Any], **kwargs):
        """
        Event called after logging.

        This method is triggered by the Trainer when new logs (metrics) are available.
        It constructs a payload with the current training state and metrics,
        and sends it to the configured server URL.
        """
        if state.is_world_process_zero:
            payload = {
                "project_name": self.project_name,
                "run_id": self.run_id,
                "event_type": "trainer_log",
                "trainer_state": self._get_trainer_state_info(state),
                "logs": logs,
                "timestamp": datetime.datetime.now().isoformat()
            }
            self._send_payload(payload, state.global_step)

    def on_train_begin(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs):
        """Event called at the beginning of training."""
        if state.is_world_process_zero:
            print(f"Training for project '{self.project_name}', run '{self.run_id}' has begun.")
            self._send_status_update("training_started", state)

    def on_train_end(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs):
        """Event called at the end of training."""
        if state.is_world_process_zero:
            print(f"Training for project '{self.project_name}', run '{self.run_id}' has ended.")
            self._send_status_update("training_finished", state)

    def on_epoch_end(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs):
        """Event called at the end of an epoch."""
        if state.is_world_process_zero:
            print(f"Epoch {int(state.epoch)} ended for project '{self.project_name}', run '{self.run_id}'.")
            self._send_status_update("epoch_ended", state)

    def _send_status_update(self, event_type: str, state: TrainerState):
        """Helper to send general status updates."""
        payload = {
            "project_name": self.project_name,
            "run_id": self.run_id,
            "event_type": event_type,
            "trainer_state": self._get_trainer_state_info(state),
            "timestamp": datetime.datetime.now().isoformat()
        }
        self._send_payload(payload, state.global_step)

    def send_custom_log(self, custom_data: Dict[str, Any]):
        """
        Sends arbitrary custom data to the remote server.

        This method can be called directly by the user at any point in their
        training script.

        Note: In a distributed training environment (e.g., with multiple GPUs),
        be mindful to call this method only from the main process to avoid
        sending duplicate logs. You can check `trainer.state.is_world_process_zero`.

        Args:
            custom_data (Dict[str, Any]): A dictionary containing the custom data
                                          to be sent.
        """
        if not isinstance(custom_data, dict):
            print("Error: custom_data must be a dictionary.")
            return

        payload = {
            "project_name": self.project_name,
            "run_id": self.run_id,
            "event_type": "custom_log",
            "custom_data": custom_data,
            "timestamp": datetime.datetime.now().isoformat()
        }
        print(f"Sending custom log for project '{self.project_name}', run '{self.run_id}'.")
        self._send_payload(payload)

# Example Usage (how you would use this in your training script):
if __name__ == "__main__":
    # --- Demonstration of MessengerLoggerCallback ---
    print("--- Demonstrating MessengerLoggerCallback instantiation ---")

    # Scenario 1: Using direct arguments
    print("\n--- Scenario 1: Using direct arguments ---")
    try:
        my_logger_direct = MessengerLoggerCallback(
            server_url="http://localhost:5000/api/logs",
            project_name="my_nlp_project_direct",
            run_id="experiment_direct_v1",
            auth_token="my_secret_direct_token",
            author_username="john.doe",
            metadata={"framework": "pytorch", "model_type": "bert-large", "hardware": "gpu"} # Direct metadata
        )
        print("Simulating log event for direct arguments...")
        dummy_args = TrainingArguments(output_dir="./tmp_output_direct")
        dummy_state = TrainerState()
        dummy_state.global_step = 10
        dummy_state.epoch = 0.1
        dummy_state.is_training = True
        dummy_state.is_world_process_zero = True # Simulate main process
        dummy_control = TrainerControl()
        dummy_logs = {"loss": 0.1234}
        my_logger_direct.on_log(dummy_args, dummy_state, dummy_control, dummy_logs)
        my_logger_direct.send_custom_log({"message": "Direct argument test complete"})
    except ValueError as e:
        print(f"Configuration Error (Direct Arguments): {e}")
    except Exception as e:
        print(f"An error occurred during direct argument demonstration: {e}")

    # Scenario 2: Using environment variables
    print("\n--- Scenario 2: Using environment variables ---")
    os.environ["MESSENGER_LOGGER_SERVER_URL"] = "http://localhost:5000/api/logs"
    os.environ["MESSENGER_LOGGER_AUTH_TOKEN"] = "my_secret_env_token"
    os.environ["MESSENGER_LOGGER_AUTHOR_USERNAME"] = "jane.smith"
    os.environ["MESSENGER_LOGGER_METADATA"] = '{"dataset": "squad", "batch_size": 32}' # JSON metadata

    try:
        my_logger_env = MessengerLoggerCallback(
            project_name="my_nlp_project_env",
            run_id="experiment_env_v1"
        )
        print("Simulating log event for environment variables...")
        dummy_args_env = TrainingArguments(output_dir="./tmp_output_env")
        dummy_state_env = TrainerState()
        dummy_state_env.global_step = 20
        dummy_state_env.epoch = 0.2
        dummy_state_env.is_training = True
        dummy_state_env.is_world_process_zero = True # Simulate main process
        dummy_control_env = TrainerControl()
        dummy_logs_env = {"loss": 0.5678, "learning_rate": 5e-5}
        my_logger_env.on_log(dummy_args_env, dummy_state_env, dummy_control_env, dummy_logs_env)
        my_logger_env.send_custom_log({"message": "Environment variable test complete"})
    except ValueError as e:
        print(f"Configuration Error (Environment Variables): {e}")
    except Exception as e:
        print(f"An error occurred during environment variable demonstration: {e}")
    finally:
        del os.environ["MESSENGER_LOGGER_SERVER_URL"]
        if "MESSENGER_LOGGER_AUTH_TOKEN" in os.environ:
            del os.environ["MESSENGER_LOGGER_AUTH_TOKEN"]
        if "MESSENGER_LOGGER_AUTHOR_USERNAME" in os.environ:
            del os.environ["MESSENGER_LOGGER_AUTHOR_USERNAME"]
        if "MESSENGER_LOGGER_METADATA" in os.environ:
            del os.environ["MESSENGER_LOGGER_METADATA"]

    # Scenario 3: Using a .env file for configuration
    print("\n--- Scenario 3: Using a .env file for configuration ---")
    dotenv_file_path = "temp.env"
    with open(dotenv_file_path, "w") as f:
        f.write("MESSENGER_LOGGER_SERVER_URL=http://localhost:5000/api/logs\n")
        f.write("MESSENGER_LOGGER_AUTH_TOKEN=my_secret_dotenv_token\n")
        f.write("MESSENGER_LOGGER_AUTHOR_USERNAME=steve.rogers\n")
        f.write("MESSENGER_LOGGER_METADATA='{\"learning_rate\": 5e-5, \"optimizer\": \"adamw\"}'\n")

    try:
        my_logger_dotenv = MessengerLoggerCallback(
            project_name="my_nlp_project_dotenv",
            run_id="experiment_dotenv_v1",
            dotenv_path=dotenv_file_path
        )
        print("Simulating log event for .env file configuration...")
        dummy_args_dotenv = TrainingArguments(output_dir="./tmp_output_dotenv")
        dummy_state_dotenv = TrainerState()
        dummy_state_dotenv.global_step = 40
        dummy_state_dotenv.epoch = 0.4
        dummy_state_dotenv.is_training = True
        dummy_state_dotenv.is_world_process_zero = True # Simulate main process
        dummy_control_dotenv = TrainerControl()
        dummy_logs_dotenv = {"loss": 0.3333}
        my_logger_dotenv.on_log(dummy_args_dotenv, dummy_state_dotenv, dummy_control_dotenv, dummy_logs_dotenv)
        my_logger_dotenv.send_custom_log({"message": ".env file test complete"})
    except ValueError as e:
        print(f"Configuration Error (.env File): {e}")
    except Exception as e:
        print(f"An error occurred during .env file demonstration: {e}")
    finally:
        if os.path.exists(dotenv_file_path):
            os.remove(dotenv_file_path)

    # Scenario 4: Server not available
    print("\n--- Scenario 4: Demonstrating server unavailability error handling ---")
    os.environ["MESSENGER_LOGGER_SERVER_URL"] = "http://localhost:9999/api/logs"
    try:
        my_logger_unavailable = MessengerLoggerCallback(
            project_name="my_nlp_project_unavailable",
            run_id="experiment_unavailable_v1"
        )
        print("Attempting to send log to unavailable server...")
        dummy_args_un = TrainingArguments(output_dir="./tmp_output_un")
        dummy_state_un = TrainerState()
        dummy_state_un.global_step = 50
        dummy_state_un.epoch = 0.5
        dummy_state_un.is_training = True
        dummy_state_un.is_world_process_zero = True # Simulate main process
        dummy_control_un = TrainerControl()
        dummy_logs_un = {"loss": 0.999}
        my_logger_unavailable.on_log(dummy_args_un, dummy_state_un, dummy_control_un, dummy_logs_un)
    except ValueError as e:
        print(f"Configuration Error (Unavailable Server): {e}")
    except Exception as e:
        print(f"An error occurred during unavailable server demonstration: {e}")
    finally:
        if "MESSENGER_LOGGER_SERVER_URL" in os.environ:
            del os.environ["MESSENGER_LOGGER_SERVER_URL"]

    print("\nDemonstration complete. Check the console output for messages.")