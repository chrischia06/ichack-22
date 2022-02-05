#!/usr/bin/env python3

import os
from aws_cdk import core

from cdk.webapp_stack import ICHackWebappStack


app = core.App()
ICHackWebappStack(app, "ICHackWebappStack",
    env=core.Environment(
      account=os.environ["AWS_ACCOUNT_ID"],
      region=os.environ["AWS_DEFAULT_REGION_NAME"])
)

app.synth()
