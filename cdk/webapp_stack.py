import os

from aws_cdk import (
    aws_autoscaling as autoscaling,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_secretsmanager as secretsmanager,
    core,
)


# CONFIG VARIABLES

# ECS Fargate task configs
EC2_INSTANCE_TYPE = os.environ["EC2_INSTANCE_TYPE"]
MIN_CAPACITY = int(os.environ["MIN_CAPACITY"])
MAX_CAPACITY = int(os.environ["MAX_CAPACITY"])
EC2_SPOT_PRICE = os.environ["EC2_SPOT_PRICE"]
SECRET_COMPLETE_ARN = os.environ["AWS_SECRET__ARN"]
TASK_CPU = int(os.environ["TASK_CPU"])
TASK_MEMORY_LIMIT = int(os.environ["TASK_MEMORY_LIMIT"])
TASK_ENV_VARS = {
    # "S3_BUCKET": os.environ["S3_BUCKET"],
    # "S3_ENDPOINT_URL": os.environ["S3_ENDPOINT_URL"],
    # "S3_REGION_NAME": os.environ["S3_REGION_NAME"],
}
TASK_SECRETS = lambda secret: {
    # Temporary solution to authenticating to S3. Should be using execution roles instead...
    "AWS_ACCESS_KEY_ID": ecs.Secret.from_secrets_manager(secret, "AWS_ACCESS_KEY_ID"),
    "AWS_SECRET_ACCESS_KEY": ecs.Secret.from_secrets_manager(secret, "AWS_SECRET_ACCESS_KEY"),
}


# CDK STACK

class ICHackWebappStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(self, "Vpc", 
            max_azs = 2, # default is all AZs in region, 
        )     

        cluster = ecs.Cluster(self, "Cluster", vpc=vpc)

        auto_scaling_group = autoscaling.AutoScalingGroup(self, "ASG",
            vpc=vpc,
            instance_type=ec2.InstanceType(EC2_INSTANCE_TYPE),
            machine_image=ec2.AmazonLinuxImage(),
            min_capacity=MIN_CAPACITY,
            max_capacity=MAX_CAPACITY,
            spot_price=EC2_SPOT_PRICE
        )

        capacity_provider = ecs.AsgCapacityProvider(self, "AsgCapacityProvider",
            auto_scaling_group=auto_scaling_group,
            enable_managed_termination_protection=False
        )

        cluster.add_asg_capacity_provider(
            provider=capacity_provider,
            spot_instance_draining=True
        )

        # Build Dockerfile from local folder and push to ECR
        image = ecs.ContainerImage.from_asset(".", file="Dockerfile")

        secret = secretsmanager.Secret.from_secret_complete_arn(self, "Secret",
            secret_complete_arn=SECRET_COMPLETE_ARN
        )

        # Use an ecs_patterns recipe to do all the rest!
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(self, "FargateService",
            cluster=cluster,
            cpu=TASK_CPU,
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=image,
                container_port=8501,
                environment=TASK_ENV_VARS,
                secrets=TASK_SECRETS(secret)
            ),
            memory_limit_mib=TASK_MEMORY_LIMIT,
            public_load_balancer=True,
            redirect_http=False
        )

        # Setup task auto-scaling
        scaling = fargate_service.service.auto_scale_task_count(
            min_capacity=MIN_CAPACITY,
            max_capacity=MAX_CAPACITY
        )
        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=75,
            scale_in_cooldown=core.Duration.seconds(60),
            scale_out_cooldown=core.Duration.seconds(60),
        )
        scaling.scale_on_memory_utilization(
            "MemoryScaling",
            target_utilization_percent=75,
            scale_in_cooldown=core.Duration.seconds(60),
            scale_out_cooldown=core.Duration.seconds(60),
        )
