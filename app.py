from flask import Flask, request, send_file, abort, jsonify, make_response
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import signers
import tempfile


app = Flask(__name__)

@app.route("/")
def hello_world():
    return'<p>Hello World</p>'

@app.route("/assinar", methods = ['POST'])
def assinar_doc():
    app.logger.info("Recebendo documento para ser assinado")
    
    pdf_recebido = request.files.get('pdf')
    if(pdf_recebido is None):
        app.logger.info("chave pdf nao foi enviada")
        return jsonify(
                   {"erro": "chave pdf nao foi enviada"}
                ), 400
        
    
    
    app.logger.info(f"Nome do documento: {pdf_recebido.filename}")
    app.logger.info(f"Tipo do arquivo: {pdf_recebido.content_type}")
    
    if(pdf_recebido.content_type != 'application/pdf'):
        app.logger.error("")
        return jsonify(
                   {"erro": "Arquivo enviado não é do tipo PDF"}
                ), 400

    certificado = request.files.get('certificado')

    if certificado is None:
        app.logger.info("chave certificado nao foi enviada")
        return jsonify(
                   {"erro": 'chave certificado nao foi enviada'}
                ), 400
    else: certificado = certificado.read()
    
    senha = request.form.get('senha')
    if senha is None:
        app.logger.info("chave senha nao foi enviada")
        return jsonify(
                   {"erro": "chave senha nao foi enviada"}
                ), 400

    nome_saida = request.form.get('nome_saida', 'assinado.pdf')

    temp = tempfile.NamedTemporaryFile()
    temp.write(certificado)
    temp.seek(0)


    
    signer = signers.SimpleSigner.load_pkcs12(
        pfx_file=temp.name, passphrase=senha.encode()
    )
    if signer is None: 
         return jsonify(
                   {"erro": "problemas com o certificado, verificar certificado enviado e senha"}
                ), 400

    temp.close()


    w = IncrementalPdfFileWriter(pdf_recebido)
    out = signers.sign_pdf(
        w, signers.PdfSignatureMetadata(field_name='Assinatura1'),
        signer=signer
    )



    return send_file(out, as_attachment=True, download_name=nome_saida)
