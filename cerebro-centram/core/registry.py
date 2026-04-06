"""
Registro Central de Skills.
Mantém catálogo de todas as skills disponíveis (Python e JS),
suas capacidades, e metadados para roteamento inteligente.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional


class SkillRuntime(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"


class SkillStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


@dataclass
class SkillInfo:
    """Metadados de uma skill registrada."""
    name: str
    description: str
    runtime: SkillRuntime
    capabilities: list[str]  # lista de capacidades para roteamento LLM
    keywords: list[str] = field(default_factory=list)  # fallback para roteamento por keyword
    module_path: Optional[str] = None  # caminho do módulo Python ou JS
    status: SkillStatus = SkillStatus.ACTIVE
    execute_fn: Optional[Callable] = None  # função de execução (skills Python)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_prompt_description(self) -> str:
        """Gera descrição para usar no prompt de roteamento do LLM."""
        return (
            f"- **{self.name}** ({self.runtime.value}): {self.description}\n"
            f"  Capacidades: {', '.join(self.capabilities)}"
        )


class SkillRegistry:
    """
    Registro central que mantém todas as skills disponíveis.
    O Cérebro Central consulta este registro para saber
    quais skills existem e o que cada uma faz.
    """

    def __init__(self):
        self._skills: dict[str, SkillInfo] = {}
        self._register_default_skills()

    def register(self, skill: SkillInfo) -> None:
        """Registra uma nova skill."""
        self._skills[skill.name] = skill

    def get(self, name: str) -> Optional[SkillInfo]:
        """Obtém uma skill pelo nome."""
        return self._skills.get(name)

    def list_active(self) -> list[SkillInfo]:
        """Lista todas as skills ativas."""
        return [s for s in self._skills.values() if s.status == SkillStatus.ACTIVE]

    def list_all(self) -> list[SkillInfo]:
        """Lista todas as skills."""
        return list(self._skills.values())

    def get_routing_prompt(self) -> str:
        """
        Gera o bloco de texto que descreve todas as skills
        para o LLM usar no roteamento inteligente.
        """
        lines = ["Skills disponíveis no sistema:\n"]
        for skill in self.list_active():
            lines.append(skill.to_prompt_description())
        return "\n".join(lines)

    def find_by_capability(self, capability: str) -> list[SkillInfo]:
        """Encontra skills que possuem uma capacidade específica."""
        capability_lower = capability.lower()
        return [
            s for s in self.list_active()
            if any(capability_lower in c.lower() for c in s.capabilities)
        ]

    def _register_default_skills(self) -> None:
        """Registra as skills padrão do sistema (JS + Python)."""

        # ── Skills Python (cerebro-centram) ──
        self.register(SkillInfo(
            name="dev",
            description="Gera projetos web completos (landing pages, sites, APIs, componentes) a partir de briefings. Cria código de produção com Next.js, TypeScript e Tailwind.",
            runtime=SkillRuntime.PYTHON,
            capabilities=[
                "gerar código", "criar landing page", "criar site", "criar API",
                "criar componente", "desenvolvimento web", "front-end", "back-end",
                "deploy", "testes automáticos", "correção de bugs", "review de código"
            ],
            keywords=["código", "site", "landing", "página", "componente", "api", "deploy",
                       "bug", "front", "back", "react", "next", "typescript"],
            module_path="skills.dev.agent",
        ))

        # ── Skills JavaScript (sistema/) ──
        self.register(SkillInfo(
            name="pesquisa_produtos",
            description="Pesquisa e valida produtos para dropshipping. Analisa fornecedores (AliExpress, CJ Dropshipping, Zendrop), calcula margens e scores de viabilidade.",
            runtime=SkillRuntime.JAVASCRIPT,
            capabilities=[
                "pesquisar produtos", "validar produto", "analisar fornecedores",
                "calcular margem", "score de produto", "nicho de mercado",
                "catálogo de produtos", "dropshipping"
            ],
            keywords=["produto", "pesquisar", "encontrar", "catálogo", "fornecedor",
                       "aliexpress", "cj dropshipping", "zendrop", "margem", "nicho"],
            module_path="sistema/skills/skill1-produtos.js",
        ))

        self.register(SkillInfo(
            name="criacao_site",
            description="Cria e edita páginas do site da loja. Gera layouts, componentes de produto, checkout e páginas responsivas para a Gadget Hub.",
            runtime=SkillRuntime.JAVASCRIPT,
            capabilities=[
                "criar página", "editar layout", "componente de produto",
                "checkout", "carrinho", "design responsivo", "HTML/CSS/JS"
            ],
            keywords=["site", "página", "layout", "componente", "design", "frontend",
                       "checkout", "carrinho", "mobile", "responsivo", "html", "css"],
            module_path="sistema/skills/skill2-site.js",
        ))

        self.register(SkillInfo(
            name="marketing",
            description="Gera estratégias de marketing digital. Cria copy para anúncios, define públicos-alvo, planeja campanhas em TikTok, Instagram, Meta Ads e Google Ads.",
            runtime=SkillRuntime.JAVASCRIPT,
            capabilities=[
                "criar anúncio", "campanha de marketing", "copy para ads",
                "público-alvo", "tráfego pago", "remarketing", "conversão",
                "TikTok Ads", "Meta Ads", "Google Ads", "email marketing"
            ],
            keywords=["anúncio", "campanha", "tiktok", "instagram", "facebook",
                       "meta ads", "google ads", "copy", "tráfego", "leads"],
            module_path="sistema/skills/skill3-marketing.js",
        ))

        self.register(SkillInfo(
            name="automacao",
            description="Configura automações para a loja. Chatbots de atendimento, processamento automático de pedidos, gestão de stock, webhooks, rastreamento e notificações.",
            runtime=SkillRuntime.JAVASCRIPT,
            capabilities=[
                "chatbot", "automação de pedidos", "gestão de stock",
                "webhooks", "integração API", "notificações automáticas",
                "rastreamento de encomendas", "atendimento automático"
            ],
            keywords=["automatizar", "automação", "bot", "chatbot", "webhook",
                       "api", "pedido", "stock", "rastreamento", "notificação"],
            module_path="sistema/skills/skill4-automacao.js",
        ))

        # ── Skill de Imagens (upsampler.com) ──
        self.register(SkillInfo(
            name="imagens",
            description="Processamento de imagens com IA via upsampler.com. Faz upscale (melhora resolução), geração de imagens de produtos, edição (remover fundo, ajustar), e criação de assets visuais para marketing e loja.",
            runtime=SkillRuntime.PYTHON,
            capabilities=[
                "upscale de imagem", "melhorar resolução", "gerar imagem de produto",
                "remover fundo", "editar imagem", "criar banner", "criar thumbnail",
                "imagem para redes sociais", "imagem para anúncio",
                "assets visuais", "foto de produto"
            ],
            keywords=["imagem", "foto", "upscale", "resolução", "banner", "thumbnail",
                       "fundo", "visual", "design", "asset", "upsampler"],
            module_path="skills.imagens.agent",
            metadata={"api_url": "https://upsampler.com", "type": "external_service"},
        ))

        # ── Skill n8n (Automação de Workflows) ──
        self.register(SkillInfo(
            name="n8n",
            description="Orquestra workflows automatizados via n8n Cloud. Conecta todas as skills em fluxos contínuos: pesquisa → conteúdo → imagens → publicação → marketing. Dispara e monitora automações.",
            runtime=SkillRuntime.PYTHON,
            capabilities=[
                "criar workflow", "disparar automação", "conectar APIs",
                "agendar tarefas", "webhook", "fluxo automatizado",
                "pipeline de conteúdo", "publicação automática"
            ],
            keywords=["workflow", "n8n", "automação", "pipeline", "agendar",
                       "fluxo", "disparar", "webhook"],
            module_path="skills.n8n.agent",
            metadata={"type": "n8n_cloud"},
        ))

        # ── Skills Python (automation/) ──
        self.register(SkillInfo(
            name="shopify",
            description="Integração direta com a Shopify API. Gere produtos, coleções, pedidos, clientes e conteúdo na loja Shopify da Gadget Hub.",
            runtime=SkillRuntime.PYTHON,
            capabilities=[
                "criar produto Shopify", "gerir coleções", "processar pedidos",
                "gerir clientes", "publicar conteúdo", "Shopify API",
                "atualizar preços", "gerir inventário"
            ],
            keywords=["shopify", "produto", "coleção", "pedido", "inventário", "loja"],
            module_path="automation.platforms.shopify",
        ))

        self.register(SkillInfo(
            name="content_generator",
            description="Gera conteúdo automatizado: descrições de produtos, posts para redes sociais, emails e textos de marketing para a Gadget Hub.",
            runtime=SkillRuntime.PYTHON,
            capabilities=[
                "gerar descrição de produto", "criar post social media",
                "escrever email marketing", "gerar conteúdo SEO"
            ],
            keywords=["conteúdo", "descrição", "post", "email", "texto"],
            module_path="automation.modules.generator",
        ))
