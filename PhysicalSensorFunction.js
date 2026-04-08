const { DefaultAzureCredential } = require("@azure/identity");
const { DigitalTwinsClient } = require("@azure/digital-twins-core");

module.exports = async function (context, eventHubMessages) {
    context.log("IoT Hub trigger function processing a message.");

    const messages = Array.isArray(eventHubMessages) ? eventHubMessages : [eventHubMessages];

    const adtInstanceUrl = "youradtinstanceurl";
    const digitalTwinId = "yourdigitaltwinid";

    const credential = new DefaultAzureCredential();
    const client = new DigitalTwinsClient(adtInstanceUrl, credential);

    for (const message of messages) {
        let payload;

        try {
            payload = typeof message === "string" ? JSON.parse(message) : message;
        } catch (err) {
            context.log.error("Invalid JSON message:", err.message);
            continue;
        }

        context.log("Received message:", JSON.stringify(payload));

        const { x, y, z } = payload;

        if (x === undefined || y === undefined || z === undefined) {
            context.log.error("Missing x, y, or z in payload.");
            continue;
        }

        context.log(`Updating digital twin '${digitalTwinId}' with Position: x=${x}, y=${y}, z=${z}`);

        const patch = [
            {
                op: "replace",
                path: "/Position",
                value: {
                    x: x,
                    y: y,
                    z: z
                }
            }
        ];

        try {
            await client.updateDigitalTwin(digitalTwinId, patch);
            context.log("Digital twin updated successfully.");
        } catch (err) {
            context.log.error("Failed to update digital twin:", err.message);
        }
    }
};
