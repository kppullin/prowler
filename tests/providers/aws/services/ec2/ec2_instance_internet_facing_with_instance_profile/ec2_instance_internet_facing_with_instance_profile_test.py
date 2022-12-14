from re import search
from unittest import mock

from boto3 import client, resource
from moto import mock_ec2, mock_iam

AWS_REGION = "us-east-1"
EXAMPLE_AMI_ID = "ami-12c6146b"


class Test_ec2_instance_internet_facing_with_instance_profile:
    @mock_ec2
    def test_ec2_no_instances(self):

        from prowler.providers.aws.lib.audit_info.audit_info import current_audit_info
        from prowler.providers.aws.services.ec2.ec2_service import EC2

        current_audit_info.audited_partition = "aws"

        with mock.patch(
            "prowler.providers.aws.services.ec2.ec2_instance_internet_facing_with_instance_profile.ec2_instance_internet_facing_with_instance_profile.ec2_client",
            new=EC2(current_audit_info),
        ):
            # Test Check
            from prowler.providers.aws.services.ec2.ec2_instance_internet_facing_with_instance_profile.ec2_instance_internet_facing_with_instance_profile import (
                ec2_instance_internet_facing_with_instance_profile,
            )

            check = ec2_instance_internet_facing_with_instance_profile()
            result = check.execute()

            assert len(result) == 0

    @mock_iam
    @mock_ec2
    def test_one_compliant_ec2(self):
        iam = client("iam", "us-west-1")
        profile_name = "fake_profile"
        _ = iam.create_instance_profile(
            InstanceProfileName=profile_name,
        )
        ec2 = resource("ec2", region_name=AWS_REGION)
        vpc = ec2.create_vpc(CidrBlock="10.0.0.0/16")
        subnet = ec2.create_subnet(VpcId=vpc.id, CidrBlock="10.0.0.0/18")
        instance = ec2.create_instances(
            ImageId=EXAMPLE_AMI_ID,
            MinCount=1,
            MaxCount=1,
            IamInstanceProfile={"Name": profile_name},
            NetworkInterfaces=[
                {
                    "DeviceIndex": 0,
                    "SubnetId": subnet.id,
                    "AssociatePublicIpAddress": False,
                }
            ],
        )[0]

        from prowler.providers.aws.lib.audit_info.audit_info import current_audit_info
        from prowler.providers.aws.services.ec2.ec2_service import EC2

        current_audit_info.audited_partition = "aws"

        with mock.patch(
            "prowler.providers.aws.services.ec2.ec2_instance_internet_facing_with_instance_profile.ec2_instance_internet_facing_with_instance_profile.ec2_client",
            new=EC2(current_audit_info),
        ):
            from prowler.providers.aws.services.ec2.ec2_instance_internet_facing_with_instance_profile.ec2_instance_internet_facing_with_instance_profile import (
                ec2_instance_internet_facing_with_instance_profile,
            )

            check = ec2_instance_internet_facing_with_instance_profile()
            result = check.execute()

            assert len(result) == 1
            assert result[0].status == "PASS"
            assert search(
                f"EC2 Instance {instance.id} is not internet facing with an instance profile",
                result[0].status_extended,
            )
            assert result[0].resource_id == instance.id

    @mock_iam
    @mock_ec2
    def test_one_non_compliant_ec2(self):
        iam = client("iam", "us-west-1")
        profile_name = "fake_profile"
        _ = iam.create_instance_profile(
            InstanceProfileName=profile_name,
        )
        ec2 = resource("ec2", region_name=AWS_REGION)
        vpc = ec2.create_vpc(CidrBlock="10.0.0.0/16")
        subnet = ec2.create_subnet(VpcId=vpc.id, CidrBlock="10.0.0.0/18")
        instance = ec2.create_instances(
            ImageId=EXAMPLE_AMI_ID,
            MinCount=1,
            MaxCount=1,
            IamInstanceProfile={"Name": profile_name},
            NetworkInterfaces=[
                {
                    "DeviceIndex": 0,
                    "SubnetId": subnet.id,
                    "AssociatePublicIpAddress": True,
                }
            ],
        )[0]

        from prowler.providers.aws.lib.audit_info.audit_info import current_audit_info
        from prowler.providers.aws.services.ec2.ec2_service import EC2

        current_audit_info.audited_partition = "aws"

        with mock.patch(
            "prowler.providers.aws.services.ec2.ec2_instance_internet_facing_with_instance_profile.ec2_instance_internet_facing_with_instance_profile.ec2_client",
            new=EC2(current_audit_info),
        ):
            from prowler.providers.aws.services.ec2.ec2_instance_internet_facing_with_instance_profile.ec2_instance_internet_facing_with_instance_profile import (
                ec2_instance_internet_facing_with_instance_profile,
            )

            check = ec2_instance_internet_facing_with_instance_profile()
            result = check.execute()

            assert len(result) == 1
            assert result[0].status == "FAIL"
            assert search(
                "is internet-facing with Instance Profile", result[0].status_extended
            )
            assert result[0].resource_id == instance.id