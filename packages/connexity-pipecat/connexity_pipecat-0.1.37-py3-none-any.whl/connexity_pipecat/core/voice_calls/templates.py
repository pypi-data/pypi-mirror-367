twiml_template_inbound = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="wss://{wss_url}/ws">
            <Parameter name="to_number" value="{to_number}" />
            <Parameter name="from_number" value="{from_number}" />
            <Parameter name="call_type" value="{call_type}" />
        </Stream>
    </Connect>
    <Pause length="40"/>
</Response>
"""


twiml_template_outbound = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="wss://{wss_url}/ws">
            <Parameter name="to_number" value="{to_number}" />
            <Parameter name="from_number" value="{from_number}" />
            <Parameter name="agent_inputs" value="{agent_inputs}" />
            <Parameter name="call_type" value="{call_type}" />
        </Stream>
    </Connect>
    <Pause length="40"/>
</Response>
"""

