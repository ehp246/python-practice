import os
import logging
import time
import json

from collections import namedtuple
from azure.eventhub import EventHubProducerClient, EventHubConsumerClient, EventData
from azure.identity import DefaultAzureCredential

EVENT_HUB_NAMESPACE = os.environ["EVENT_HUB_NAMESPACE"]
EVENT_HUB_NAME = os.environ["EVENT_HUB_NAME"]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.WARN)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

credential = DefaultAzureCredential()

producerClient = EventHubProducerClient(        
    fully_qualified_namespace=EVENT_HUB_NAMESPACE,
    eventhub_name=EVENT_HUB_NAME,
    credential=credential,)

consumeClient = EventHubConsumerClient(
    fully_qualified_namespace=EVENT_HUB_NAMESPACE,
    eventhub_name=EVENT_HUB_NAME,
    consumer_group="python-practice",
    credential=credential,
)

def on_event(partition_context, event):
    key = event.partition_key.decode('UTF-8')
    value = json.loads(event.body_as_str(encoding="UTF-8"), object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
    logger.debug("Received event:%s, %s", key, value)
    if (key == "MmmJobCreated"):
        producerClient.send_event(EventData(["id", value.id]), partition_key="MmmJobExecutionStarted")
        time.sleep(10)
        producerClient.send_event(EventData("MmmJobExecutionCompleted"), partition_key="MmmJobExecutionStarted")
    else:
        logger.debug("Ignored")

def main():
    # Call the receive method. Read from the beginning of the partition
    # (starting_position: "-1")
    consumeClient.receive(on_event=on_event, starting_position="-1")

    # Close credential when no longer needed.
    credential.close()

if __name__ == "__main__":
    # Run the main method.
    main()