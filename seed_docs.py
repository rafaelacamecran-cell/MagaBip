from app import create_app
from extensions import db
from models import TechnicalDoc

# Lista de manuais para semear o banco de dados
DOCUMENTACAO = [
    {
        "title": "Como realizar o Hard Reset no Coletor Zebra",
        "category": "Coletores",
        "tags": "reset, travamento, tela preta",
        "content": """
        <strong>Problema:</strong> O coletor travou na tela inicial ou a tela ficou totalmente preta.
        <br><br>
        <strong>Solução (Hard Reset):</strong>
        <ol>
            <li>Pressione e segure simultaneamente o botão de <b>Ligar/Desligar</b> e o botão de <b>Aumentar Volume</b>.</li>
            <li>Mantenha pressionado por aproximadamente 10 a 15 segundos.</li>
            <li>Solte os botões assim que o logotipo da Zebra aparecer na tela.</li>
            <li>Aguarde a inicialização completa do sistema Android.</li>
        </ol>
        <em>Nota: Este procedimento não apaga os dados gravados no aparelho, apenas força a reinicialização física.</em>
        """
    },
    {
        "title": "Troca de Bobina e Calibração - Impressora Zebra",
        "category": "Impressoras",
        "tags": "papel, bobina, calibração, erro de mídia",
        "content": """
        <strong>Problema:</strong> A impressora está piscando a luz vermelha de erro (Media Out) após a troca da bobina.
        <br><br>
        <strong>Solução (Calibração Rápida):</strong>
        <ol>
            <li>Abra a tampa superior da impressora e verifique se a bobina está bem encaixada nos guias.</li>
            <li>Feche a tampa até ouvir o 'clique' de travamento de ambos os lados.</li>
            <li>Pressione e segure o botão <b>FEED (Avançar)</b>.</li>
            <li>Observe a luz indicadora: ela piscará uma vez, depois duas vezes. Solte o botão imediatamente após a segunda piscada.</li>
            <li>A impressora irá ejetar de 2 a 3 etiquetas em branco para medir o tamanho correto e a luz ficará verde.</li>
        </ol>
        """
    },
    {
        "title": "O que fazer quando o Rádio não conecta no canal?",
        "category": "Rádios",
        "tags": "sinal, chiado, canal, comunicação",
        "content": """
        <strong>Problema:</strong> O rádio está apenas chiando ou não consegue se comunicar com o restante da equipe.
        <br><br>
        <strong>Solução:</strong>
        <ul>
            <li><strong>Verifique o Canal:</strong> Gire o botão seletor de canal (geralmente o botão do meio) e certifique-se de que está no mesmo canal que a sua equipe (Ex: Canal 1 para Expedição).</li>
            <li><strong>Bateria:</strong> Rádios com bateria muito fraca cortam a transmissão para economizar energia. Coloque na base de carregamento e verifique se a luz fica vermelha (carregando).</li>
            <li><strong>Antena:</strong> Verifique se a antena não está frouxa. Tente rosqueá-la suavemente no sentido horário. Se estiver quebrada, leve imediatamente ao TI.</li>
        </ul>
        """
    },
    {
        "title": "Boas práticas de uso da Transpaleteira Elétrica",
        "category": "Transpaleteiras",
        "tags": "segurança, bateria, carregamento",
        "content": """
        <strong>Regras de Ouro:</strong>
        <br><br>
        <ol>
            <li><strong>Sempre desligue a chave geral</strong> (botão vermelho de emergência) ao estacionar a máquina.</li>
            <li>Não deixe a bateria zerar completamente. O ideal é colocar para carregar quando atingir 20% (faixa vermelha).</li>
            <li>Ao colocar na tomada, certifique-se de que o plugue está bem encaixado para evitar curto-circuito.</li>
            <li>Se a máquina apresentar falha na elevação dos garfos, reporte o problema imediatamente e <b>não tente usar</b> para evitar acidentes.</li>
        </ol>
        """
    }
]

def seed_documents():
    """Função para inserir a documentação no Banco de Dados."""
    app = create_app()
    with app.app_context():
        print("Limpando banco de dados de Documentação Técnica...")
        db.session.query(TechnicalDoc).delete()
        db.session.commit()

        print("Semeando manuais técnicos...")
        
        count = 0
        for doc in DOCUMENTACAO:
            novo_doc = TechnicalDoc(
                title=doc['title'],
                category=doc['category'],
                tags=doc['tags'],
                content=doc['content']
            )
            db.session.add(novo_doc)
            count += 1
        
        db.session.commit()
        print(f"Sucesso! Total: {TechnicalDoc.query.count()} manuais cadastrados no banco de dados.")

if __name__ == "__main__":
    seed_documents()