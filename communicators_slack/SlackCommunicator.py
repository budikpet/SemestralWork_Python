import os
from slack import WebClient
from typing import Dict
from algorithm_tester_common.tester_dataclasses import Communicator
from algorithm_tester_common.tester_dataclasses import AlgTesterContext

class SlackCommunicator(Communicator):
    
    def __init__(self):
        self.slack_web_client = WebClient(token=os.environ['slack_access_token'])
        self.main_msg_ts = None

    def get_name(self):
        return "Slack"

    def notify_instance_computed(self, context: AlgTesterContext, last_solution: Dict[str, object], num_of_instances_done: int):
        """
        The Slack communicator is notified when an instance is computed.
        
        Arguments:
            context {AlgTesterContext} -- [description]
            last_solution {Dict[str, object]} -- [description]
            num_of_instances_done {int} -- [description]
        """
        output_filename: str = last_solution.get("output_file_name")
        print(f'Output file: {context.output_dir}/{output_filename}')
        print(f'Instances remaining: {num_of_instances_done}/{context.num_of_instances}')

        message = {
            "username": "AlgorithmTester_Bot",
            "channel": os.environ['slack_channel_id'],
            "text": f"Test message. Progress: {num_of_instances_done}/{context.num_of_instances} instances done."
        }

        if self.main_msg_ts is None:
            response = self.slack_web_client.chat_postMessage(**message)
            self.main_msg_ts = response["ts"]
        else:
            message = {
                "username": "AlgorithmTester_Bot",
                "as_user": "AlgorithmTester_Bot",
                "ts": self.main_msg_ts,
                "channel": os.environ['slack_channel_id'],
                "text": f"Test message. Progress: {num_of_instances_done}/{context.num_of_instances} instances done."
            }
            response = self.slack_web_client.chat_update(**message)
        
        print