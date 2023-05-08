#from django.test import SimpleTestCase

#from robber import expect
#from moto import mock_s3, mock_lambda

#from shared.aws import aws


#class AWSTestCase(SimpleTestCase):
#    @mock_s3
#    @mock_lambda
#    def test_aws_lazy_init_s3_and_lambda_client(self):
#        expect(aws._s3).to.be.none()
#        expect(aws._lambda_client).to.be.none()
#
#        s3 = aws.s3
#        lambda_client = aws.lambda_client
#
#        expect(aws._s3).to.be.eq(s3)
#        expect(aws._lambda_client).to.be.eq(lambda_client)
#
#        s3_2 = aws.s3
#        lambda_client_2 = aws.lambda_client
#        expect(id(s3_2)).to.be.eq(id(s3))
#        expect(id(lambda_client_2)).to.be.eq(id(lambda_client))
