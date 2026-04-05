"""
criar_produtos.py — Cria os 12 produtos + 4 colecções na loja Shopify
Uso: cd automation && pip install requests python-dotenv && python criar_produtos.py
"""
import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

STORE = os.getenv("SHOPIFY_STORE_NAME", "gadget-hub-72955")
TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN", os.getenv("SHOPIFY_CLIENT_SECRET", ""))
API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2026-01")
BASE = f"https://{STORE}.myshopify.com/admin/api/{API_VERSION}"
HEADERS = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}


def api(method, endpoint, data=None):
    url = f"{BASE}/{endpoint}"
    r = requests.request(method, url, headers=HEADERS, json=data, timeout=30)
    limit = r.headers.get("X-Shopify-Shop-Api-Call-Limit", "0/40")
    used = int(limit.split("/")[0])
    if used > 30:
        time.sleep(2)
    if r.status_code >= 400:
        print(f"  ERRO {r.status_code}: {r.text[:200]}")
        return None
    return r.json() if r.text else {}


# =============================================
# COLECÇÕES
# =============================================
COLECCOES = [
    {"title": "Casa Inteligente", "body_html": "<p>Transforma a tua casa com tecnologia inteligente. Tomadas WiFi, câmaras, sensores e muito mais — tudo controlável pelo telemóvel.</p>", "sort_order": "best-selling"},
    {"title": "Áudio & Som", "body_html": "<p>Fones, colunas e acessórios de áudio com qualidade premium. Bluetooth 5.3, cancelamento de ruído e bateria de longa duração.</p>", "sort_order": "best-selling"},
    {"title": "Acessórios Tech", "body_html": "<p>Carregadores, hubs, power banks e periféricos essenciais para o teu dia-a-dia tecnológico.</p>", "sort_order": "best-selling"},
    {"title": "Electrónicos", "body_html": "<p>Monitores, dispositivos portáteis e gadgets electrónicos de última geração.</p>", "sort_order": "best-selling"},
]


# =============================================
# 12 PRODUTOS
# =============================================
PRODUTOS = [
    {
        "title": "Tomada Inteligente WiFi 16A — Controlo por Voz e App",
        "body_html": """<h2>Controla Tudo com o Teu Telemóvel</h2>
<p>A <strong>Tomada Inteligente WiFi 16A</strong> permite-te ligar e desligar qualquer dispositivo da tua casa a partir do telemóvel, onde quer que estejas. Compatível com <strong>Alexa</strong> e <strong>Google Home</strong>.</p>
<h3>Características</h3>
<ul>
<li>Controlo remoto via app Smart Life</li>
<li>Compatível com Alexa, Google Assistant e Siri Shortcuts</li>
<li>Temporizador e agendamento programável</li>
<li>Monitorização de consumo energético em tempo real</li>
<li>Suporta até 16A / 3680W</li>
<li>Configuração fácil em 2 minutos</li>
</ul>
<h3>Ideal Para</h3>
<p>Candeeiros, aquecedores, ventoinhas, máquinas de café — qualquer aparelho com ficha eléctrica.</p>""",
        "vendor": "Gadget Hub",
        "product_type": "Casa Inteligente",
        "tags": "smart-home, wifi, alexa, google-home, tomada, automação",
        "variants": [{"price": "29.90", "compare_at_price": "41.90", "sku": "GH-PLUG-001", "inventory_management": "shopify", "inventory_quantity": 100}],
        "images": [{"src": "https://placehold.co/800x800/1a1a2e/00d4ff?text=Smart+Plug+WiFi"}],
        "status": "active",
    },
    {
        "title": "Lâmpada RGB Smart E27 — 16 Milhões de Cores",
        "body_html": """<h2>Iluminação Inteligente Para Todos os Momentos</h2>
<p>A <strong>Lâmpada RGB Smart E27</strong> transforma qualquer divisão com 16 milhões de cores. Controla por voz ou pela app — cria ambientes perfeitos para trabalhar, relaxar ou festejar.</p>
<h3>Características</h3>
<ul>
<li>16 milhões de cores + branco quente e frio</li>
<li>Controlo por voz (Alexa, Google Home)</li>
<li>App com temporizador e cenas pré-definidas</li>
<li>12W equivale a 100W convencional</li>
<li>Casquilho E27 universal</li>
<li>Consumo energético classe A+</li>
</ul>""",
        "vendor": "Gadget Hub",
        "product_type": "Casa Inteligente",
        "tags": "smart-home, iluminação, rgb, alexa, lâmpada",
        "variants": [{"price": "24.90", "compare_at_price": "34.90", "sku": "GH-LAMP-002", "inventory_management": "shopify", "inventory_quantity": 150}],
        "images": [{"src": "https://placehold.co/800x800/1a1a2e/7c3aed?text=Lâmpada+RGB+Smart"}],
        "status": "active",
    },
    {
        "title": "Câmara WiFi 1080p — Vigilância 360° com Visão Noturna",
        "body_html": """<h2>Segurança Total, 24 Horas Por Dia</h2>
<p>A <strong>Câmara WiFi 1080p</strong> oferece vigilância completa com rotação 360°, visão noturna infravermelha e detecção de movimento com alerta no telemóvel.</p>
<h3>Características</h3>
<ul>
<li>Resolução Full HD 1080p</li>
<li>Rotação 360° horizontal + 90° vertical</li>
<li>Visão noturna até 10 metros</li>
<li>Detecção de movimento com notificação push</li>
<li>Áudio bidireccional</li>
<li>Armazenamento em cartão SD ou cloud</li>
<li>App gratuita para iOS e Android</li>
</ul>""",
        "vendor": "Gadget Hub",
        "product_type": "Casa Inteligente",
        "tags": "smart-home, câmara, segurança, wifi, vigilância",
        "variants": [{"price": "49.90", "compare_at_price": "69.90", "sku": "GH-CAM-003", "inventory_management": "shopify", "inventory_quantity": 80}],
        "images": [{"src": "https://placehold.co/800x800/1a1a2e/4ade80?text=Câmara+WiFi+1080p"}],
        "status": "active",
    },
    {
        "title": "Fones TWS Bluetooth 5.3 — Cancelamento de Ruído Activo",
        "body_html": """<h2>Som Premium Sem Fios</h2>
<p>Os <strong>Fones TWS Bluetooth 5.3</strong> oferecem som cristalino com cancelamento de ruído activo (ANC), 30 horas de bateria total e resistência à água IPX5.</p>
<h3>Características</h3>
<ul>
<li>Bluetooth 5.3 com conexão estável</li>
<li>Cancelamento de ruído activo (ANC)</li>
<li>30h de bateria (6h + 24h no estojo)</li>
<li>Resistência à água IPX5</li>
<li>Modo transparência para ouvir o ambiente</li>
<li>Microfone HD para chamadas</li>
<li>Controlo táctil</li>
</ul>""",
        "vendor": "Gadget Hub",
        "product_type": "Áudio",
        "tags": "áudio, fones, bluetooth, tws, anc, wireless",
        "variants": [{"price": "69.90", "compare_at_price": "97.90", "sku": "GH-TWS-004", "inventory_management": "shopify", "inventory_quantity": 120}],
        "images": [{"src": "https://placehold.co/800x800/1a1a2e/00d4ff?text=Fones+TWS+BT+5.3"}],
        "status": "active",
    },
    {
        "title": "Coluna Bluetooth Portátil 20W — Som 360° à Prova de Água",
        "body_html": """<h2>Leva a Música Para Todo o Lado</h2>
<p>A <strong>Coluna Bluetooth Portátil</strong> com 20W de potência e som 360° é a companheira perfeita para praia, piscina ou casa. Resistente à água IPX7.</p>
<h3>Características</h3>
<ul>
<li>Potência de 20W com som 360°</li>
<li>Resistência à água IPX7 (submersível)</li>
<li>12 horas de autonomia</li>
<li>Bluetooth 5.0 com alcance de 15m</li>
<li>TWS: emparelha duas colunas para som stereo</li>
<li>Slot para cartão micro SD</li>
</ul>""",
        "vendor": "Gadget Hub",
        "product_type": "Áudio",
        "tags": "áudio, coluna, bluetooth, portátil, waterproof",
        "variants": [{"price": "59.90", "compare_at_price": "83.90", "sku": "GH-SPK-005", "inventory_management": "shopify", "inventory_quantity": 90}],
        "images": [{"src": "https://placehold.co/800x800/1a1a2e/7c3aed?text=Coluna+BT+20W"}],
        "status": "active",
    },
    {
        "title": "Hub USB-C 7 em 1 — HDMI 4K + Carregamento 100W PD",
        "body_html": """<h2>Expande o Teu Portátil Ao Máximo</h2>
<p>O <strong>Hub USB-C 7 em 1</strong> transforma uma porta USB-C em 7 conexões: HDMI 4K, USB 3.0, leitor SD, e carregamento rápido 100W PD.</p>
<h3>Portas</h3>
<ul>
<li>1x HDMI 4K@60Hz</li>
<li>2x USB 3.0 (5Gbps)</li>
<li>1x USB-C PD 100W (carregamento)</li>
<li>1x Leitor SD</li>
<li>1x Leitor micro SD</li>
<li>1x USB 2.0</li>
</ul>
<h3>Compatibilidade</h3>
<p>MacBook, iPad Pro, Surface, portáteis Windows com USB-C, Samsung DeX.</p>""",
        "vendor": "Gadget Hub",
        "product_type": "Acessórios",
        "tags": "acessórios, hub, usb-c, hdmi, macbook, produtividade",
        "variants": [{"price": "39.90", "compare_at_price": "55.90", "sku": "GH-HUB-006", "inventory_management": "shopify", "inventory_quantity": 70}],
        "images": [{"src": "https://placehold.co/800x800/1a1a2e/00d4ff?text=Hub+USB-C+7+em+1"}],
        "status": "active",
    },
    {
        "title": "Carregador Wireless 15W — Carga Rápida Qi",
        "body_html": """<h2>Carrega Sem Fios, Sem Complicações</h2>
<p>O <strong>Carregador Wireless 15W</strong> com tecnologia Qi oferece carregamento rápido para iPhone e Android. Basta pousar o telemóvel.</p>
<h3>Características</h3>
<ul>
<li>Carregamento rápido 15W (Android) / 7.5W (iPhone)</li>
<li>Compatível com todos os dispositivos Qi</li>
<li>LED indicador discreto</li>
<li>Protecção contra sobreaquecimento</li>
<li>Design ultra-slim (9mm de espessura)</li>
<li>Base anti-deslizante</li>
</ul>""",
        "vendor": "Gadget Hub",
        "product_type": "Acessórios",
        "tags": "acessórios, carregador, wireless, qi, iphone, android",
        "variants": [{"price": "34.90", "compare_at_price": "48.90", "sku": "GH-CHG-007", "inventory_management": "shopify", "inventory_quantity": 130}],
        "images": [{"src": "https://placehold.co/800x800/1a1a2e/4ade80?text=Carregador+Wireless"}],
        "status": "active",
    },
    {
        "title": "Power Bank 20000mAh — Carga Rápida 22.5W com Display",
        "body_html": """<h2>Energia Para o Dia Todo</h2>
<p>O <strong>Power Bank 20000mAh</strong> carrega o teu telemóvel até 5 vezes com carga rápida 22.5W. Display LCD mostra a bateria restante.</p>
<h3>Características</h3>
<ul>
<li>Capacidade: 20000mAh</li>
<li>Carga rápida 22.5W (output)</li>
<li>3 portas: USB-A + USB-A + USB-C</li>
<li>Carrega 2 dispositivos em simultâneo</li>
<li>Display LCD com percentagem de bateria</li>
<li>Design ultra-slim (15mm)</li>
<li>Protecção contra curto-circuito</li>
</ul>""",
        "vendor": "Gadget Hub",
        "product_type": "Acessórios",
        "tags": "acessórios, power-bank, bateria, portátil, carregamento",
        "variants": [{"price": "49.90", "compare_at_price": "69.90", "sku": "GH-PWR-008", "inventory_management": "shopify", "inventory_quantity": 100}],
        "images": [{"src": "https://placehold.co/800x800/1a1a2e/7c3aed?text=Power+Bank+20000mAh"}],
        "status": "active",
    },
    {
        "title": "Aspirador Robô Smart — Mapeamento Laser e App WiFi",
        "body_html": """<h2>Limpeza Inteligente e Autónoma</h2>
<p>O <strong>Aspirador Robô Smart</strong> com mapeamento laser LDS navega pela tua casa com precisão. Controla tudo pela app ou por voz com Alexa.</p>
<h3>Características</h3>
<ul>
<li>Mapeamento laser LDS com navegação inteligente</li>
<li>App WiFi com mapa em tempo real</li>
<li>Compatível com Alexa e Google Home</li>
<li>Sucção potente: 2700Pa</li>
<li>120 minutos de autonomia</li>
<li>Retorno automático à base de carregamento</li>
<li>Aspira e lava em simultâneo</li>
<li>Ultra-silencioso: apenas 55dB</li>
</ul>""",
        "vendor": "Gadget Hub",
        "product_type": "Casa Inteligente",
        "tags": "smart-home, aspirador, robô, alexa, limpeza, automação",
        "variants": [{"price": "189.90", "compare_at_price": "265.90", "sku": "GH-VAC-009", "inventory_management": "shopify", "inventory_quantity": 40}],
        "images": [{"src": "https://placehold.co/800x800/1a1a2e/00d4ff?text=Aspirador+Robô+Smart"}],
        "status": "active",
    },
    {
        "title": "Rato Sem Fio Silencioso — 2.4GHz Ultra-Confortável",
        "body_html": """<h2>Cliques Silenciosos, Conforto Total</h2>
<p>O <strong>Rato Sem Fio Silencioso</strong> com redução de 99% do ruído é perfeito para escritório e trabalho nocturno. Bateria até 12 meses.</p>
<h3>Características</h3>
<ul>
<li>Clique silencioso: redução de ruído de 99%</li>
<li>Conexão wireless 2.4GHz com nano-receptor USB</li>
<li>Sensibilidade ajustável: 800/1200/1600 DPI</li>
<li>Bateria: 1x AA dura até 12 meses</li>
<li>Design ergonómico para uso prolongado</li>
<li>Compatível com Windows, Mac, Linux</li>
</ul>""",
        "vendor": "Gadget Hub",
        "product_type": "Acessórios",
        "tags": "acessórios, rato, mouse, wireless, silencioso, escritório",
        "variants": [{"price": "29.90", "compare_at_price": "41.90", "sku": "GH-MOU-010", "inventory_management": "shopify", "inventory_quantity": 110}],
        "images": [{"src": "https://placehold.co/800x800/1a1a2e/4ade80?text=Rato+Silencioso"}],
        "status": "active",
    },
    {
        "title": "Teclado Bluetooth Ultra-slim — Multi-dispositivo",
        "body_html": """<h2>Escreve Em Qualquer Dispositivo</h2>
<p>O <strong>Teclado Bluetooth Ultra-slim</strong> conecta até 3 dispositivos em simultâneo e alterna com um toque. Recarregável via USB-C.</p>
<h3>Características</h3>
<ul>
<li>Bluetooth 5.0 multi-dispositivo (até 3)</li>
<li>Compatível com Windows, Mac, iOS e Android</li>
<li>Recarga via USB-C (2h = 90 dias de uso)</li>
<li>Teclas silenciosas tipo tesoura</li>
<li>Design ultra-slim: apenas 6mm</li>
<li>Layout compacto com teclas de atalho</li>
</ul>""",
        "vendor": "Gadget Hub",
        "product_type": "Acessórios",
        "tags": "acessórios, teclado, bluetooth, wireless, multi-dispositivo",
        "variants": [{"price": "44.90", "compare_at_price": "62.90", "sku": "GH-KEY-011", "inventory_management": "shopify", "inventory_quantity": 85}],
        "images": [{"src": "https://placehold.co/800x800/1a1a2e/7c3aed?text=Teclado+BT+Slim"}],
        "status": "active",
    },
    {
        "title": "Monitor Portátil 15.6\" FHD — USB-C Plug & Play",
        "body_html": """<h2>O Teu Segundo Ecrã, Onde Quiseres</h2>
<p>O <strong>Monitor Portátil 15.6"</strong> com resolução Full HD é o companheiro perfeito para trabalho remoto, gaming e apresentações. Plug & Play via USB-C.</p>
<h3>Características</h3>
<ul>
<li>Ecrã IPS 15.6" Full HD (1920x1080)</li>
<li>Ângulo de visão 178°</li>
<li>Conexão USB-C (vídeo + alimentação)</li>
<li>Mini HDMI para compatibilidade extra</li>
<li>Colunas integradas</li>
<li>Peso: apenas 800g</li>
<li>Capa protectora com suporte incluída</li>
</ul>
<h3>Ideal Para</h3>
<p>Trabalho remoto, programação, design, gaming portátil, apresentações.</p>""",
        "vendor": "Gadget Hub",
        "product_type": "Electrónicos",
        "tags": "electrónicos, monitor, portátil, usb-c, trabalho-remoto",
        "variants": [{"price": "149.90", "compare_at_price": "209.90", "sku": "GH-MON-012", "inventory_management": "shopify", "inventory_quantity": 50}],
        "images": [{"src": "https://placehold.co/800x800/1a1a2e/00d4ff?text=Monitor+15.6+FHD"}],
        "status": "active",
    },
]

CATEGORIA_MAP = {
    "Casa Inteligente": 0,
    "Áudio": 1,
    "Acessórios": 2,
    "Electrónicos": 3,
}


def main():
    print("=" * 55)
    print("  GADGET HUB — Criação de Produtos no Shopify")
    print("=" * 55)

    if not TOKEN:
        print("\n  ERRO: Token não encontrado no .env")
        print("  Certifica-te que SHOPIFY_ACCESS_TOKEN está definido.")
        return

    # 1. Testar conexão
    print(f"\n  Loja: {STORE}")
    print(f"  API: {API_VERSION}")
    print("\n  A testar conexão...")
    info = api("GET", "shop.json")
    if not info:
        print("  ERRO: Não foi possível ligar ao Shopify.")
        return
    shop = info.get("shop", {})
    print(f"  Conectado! Loja: {shop.get('name', '?')} ({shop.get('domain', '?')})")

    # 2. Criar colecções
    print(f"\n  A criar {len(COLECCOES)} colecções...")
    coleccao_ids = {}
    for col in COLECCOES:
        result = api("POST", "custom_collections.json", {"custom_collection": col})
        if result:
            c = result.get("custom_collection", {})
            coleccao_ids[col["title"]] = c.get("id")
            print(f"    ✓ {col['title']} (ID: {c.get('id')})")
        time.sleep(0.5)

    # 3. Criar produtos
    print(f"\n  A criar {len(PRODUTOS)} produtos...")
    produto_ids = []
    for i, prod in enumerate(PRODUTOS, 1):
        result = api("POST", "products.json", {"product": prod})
        if result:
            p = result.get("product", {})
            produto_ids.append({"id": p.get("id"), "type": prod["product_type"]})
            preco = prod["variants"][0]["price"]
            print(f"    ✓ {i:2d}. {prod['title'][:50]}... — €{preco}")
        else:
            print(f"    ✗ {i:2d}. FALHOU: {prod['title'][:50]}...")
        time.sleep(0.5)

    # 4. Associar produtos a colecções
    print(f"\n  A associar produtos às colecções...")
    for prod_info in produto_ids:
        cat = prod_info["type"]
        col_id = coleccao_ids.get(cat)
        if col_id:
            api("POST", "collects.json", {"collect": {"product_id": prod_info["id"], "collection_id": col_id}})
    print("    ✓ Produtos associados às colecções")

    # 5. Resumo
    print("\n" + "=" * 55)
    print("  CONCLUÍDO!")
    print(f"  {len(produto_ids)} produtos criados")
    print(f"  {len(coleccao_ids)} colecções criadas")
    print(f"\n  Acede à tua loja: https://{STORE}.myshopify.com")
    print(f"  Admin: https://{STORE}.myshopify.com/admin/products")
    print("=" * 55)


if __name__ == "__main__":
    main()
