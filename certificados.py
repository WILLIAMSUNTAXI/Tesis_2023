import os
from OpenSSL import crypto


def verify_certificate_with_private_key(certificate, private_key):
    try:
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, certificate)
        private_key = crypto.load_privatekey(crypto.FILETYPE_PEM, private_key)
        crypto.verify(cert, private_key, "sha256")
        return True
    except:
        return False

def main():
    # directory = "certificados"
    # for filename in os.listdir(directory):
    #     if filename.endswith(".pem"):
    #         cert_file = os.path.join(directory, filename)
    #         create_user(cert_file)
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, open('certificados/empresa1_certificate.pem', 'rb').read())
    subject = cert.get_subject()
    username = subject.CN
    email = subject.emailAddress
    print("Username: ", username)
    print("Email: ", email)




if __name__ == "__main__":
    main()
