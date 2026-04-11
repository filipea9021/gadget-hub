"""
CIS — Bot Telegram (v2)
Interface com o usuário. Fase 2: /resultado, /aprender, /status com stats reais.
"""

import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, CallbackQueryHandler
)
from core.orchestrator import orchestrator
from core.config import config
from memory.store import save_content, get_history, get_last_content_id, get_scraping_stats


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

async def _send_chunks(update: Update, text: str, parse_mode: str = None) -> None:
    """Envia texto em chunks de 4000 chars (limite do Telegram)."""
    for i in range(0, len(text), 4000):
        kwargs = {"text": text[i:i+4000]}
        if parse_mode:
            kwargs["parse_mode"] = parse_mode
        await update.message.reply_text(**kwargs)


def _format_output(output: dict) -> str:
    """Formata a saída do pipeline de forma legível."""
    lines = []

    # Criação
    if "creation" in output:
        creation = output["creation"]
        final = creation.get("final", {})
        script = final.get("refined_script", creation.get("script", {}))

        if script:
            lines.append("✍️ *ROTEIRO*")
            lines.append(f"*Título:* {script.get('title', '—')}")
            lines.append(f"*Hook:* {script.get('hook', '—')}")
            lines.append(f"*Duração:* {script.get('estimated_duration', '—')}")
            lines.append("")

            sections = script.get("sections", [])
            for sec in sections[:5]:
                lines.append(f"⏱ {sec.get('timestamp', '')} — {sec.get('narration', '')[:120]}")

            if script.get("cta"):
                lines.append(f"\n📢 *CTA:* {script.get('cta')}")

            score = final.get("quality_score", "—")
            viral = final.get("viral_potential", "—")
            lines.append(f"\n⭐ Score: {score}/10 | Potencial: {viral}")

    # Research
    if "research" in output:
        research = output["research"]
        lines.append("🔍 *PESQUISA*")
        source = research.get("data_source", "claude_knowledge")
        samples = research.get("samples_used", 0)
        if source == "youtube_api":
            lines.append(f"📊 {samples} vídeos reais analisados via YouTube API")
        else:
            lines.append("🧠 Análise baseada no conhecimento do Claude")

        analysis = research.get("analysis", {})
        if analysis.get("summary"):
            lines.append(f"\n{analysis['summary']}")

    # Optimization
    if "optimization" in output:
        opt = output["optimization"]
        seo = opt.get("seo", {})
        if seo.get("titles"):
            lines.append("\n🎯 *TÍTULOS SUGERIDOS*")
            for t in seo["titles"][:3]:
                lines.append(f"• {t}")
        if seo.get("hashtags"):
            lines.append(f"\n🏷 {' '.join(seo['hashtags'][:10])}")

    return "\n".join(lines) if lines else json.dumps(output, indent=2, ensure_ascii=False)[:3000]


# ------------------------------------------------------------------
# Handlers
# ------------------------------------------------------------------

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧠 *CIS — Content Intelligence System v2*\n\n"
        "Sistema que aprende com dados reais e melhora a cada uso.\n\n"
        "*Comandos:*\n"
        "/criar \\[pedido\\] — cria conteúdo do zero\n"
        "/full \\[pedido\\] — pipeline completo \\(pesquisa + criação + SEO\\)\n"
        "/pesquisar \\[nicho\\] — só pesquisa e análise\n"
        "/otimizar \\[conteúdo\\] — otimiza para publicação\n"
        "/aprender \\[nicho\\] — roda ciclo de aprendizado autônomo\n"
        "/resultado — reporta performance do último conteúdo\n"
        "/historico — últimos conteúdos gerados\n"
        "/status — estatísticas do sistema\n\n"
        "Ou manda seu pedido diretamente sem comando.",
        parse_mode="MarkdownV2"
    )


async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handler principal: qualquer mensagem livre vai para o orquestrador."""
    msg = update.message.text
    await update.message.reply_text("⏳ Processando...")

    try:
        result = await orchestrator.execute(msg)
        output = result.get("outputs", {})
        formatted = _format_output(output)

        await _send_chunks(update, formatted, parse_mode="Markdown")

        # Salva na memória
        task_ctx = result.get("context")
        if task_ctx:
            content_id = save_content(
                msg,
                task_ctx.mode.value,
                task_ctx.niche,
                task_ctx.platform,
                output
            )
            # Guarda ID no contexto do usuário para /resultado
            ctx.user_data["last_content_id"] = content_id
            ctx.user_data["last_niche"] = task_ctx.niche
            ctx.user_data["last_platform"] = task_ctx.platform

    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {e}")


async def cmd_resultado(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    /resultado [views] [likes] [comentarios] [compartilhamentos]
    Ex: /resultado 50000 3200 450 890
    """
    args = ctx.args or []

    content_id = ctx.user_data.get("last_content_id") or get_last_content_id()
    niche = ctx.user_data.get("last_niche", "geral")
    platform = ctx.user_data.get("last_platform", "instagram")

    if not content_id:
        await update.message.reply_text(
            "❌ Nenhum conteúdo gerado ainda nesta sessão.\n"
            "Gere um conteúdo primeiro com /criar ou /full."
        )
        return

    if len(args) < 2:
        await update.message.reply_text(
            "📊 Reporte a performance do seu último conteúdo:\n\n"
            "Uso: `/resultado [views] [likes] [comentários] [shares]`\n"
            "Ex: `/resultado 50000 3200 450 890`\n\n"
            "Mínimo: views e likes.",
            parse_mode="Markdown"
        )
        return

    try:
        views = int(args[0])
        likes = int(args[1])
        comments = int(args[2]) if len(args) > 2 else 0
        shares = int(args[3]) if len(args) > 3 else 0
    except ValueError:
        await update.message.reply_text("❌ Números inválidos. Exemplo: /resultado 50000 3200 450 890")
        return

    await update.message.reply_text("📈 Registrando performance e evoluindo DNA...")

    try:
        from dna_evolver import dna_evolver
        result = await dna_evolver.evolve_from_feedback(
            content_history_id=content_id,
            views=views,
            likes=likes,
            comments=comments,
            shares=shares,
            platform=platform,
            niche=niche,
        )

        tier_emoji = {"viral": "🚀", "good": "✅", "average": "📊", "poor": "📉"}.get(result["tier"], "📊")
        await update.message.reply_text(
            f"{tier_emoji} *{result['tier'].upper()}*\n\n"
            f"{result['message']}\n\n"
            f"Ajuste no DNA: {result['adjustment']}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao registrar: {e}")


async def cmd_aprender(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    /aprender [nicho]
    Roda ciclo de aprendizado autônomo: scrape → DNA extraction.
    """
    niche = " ".join(ctx.args) if ctx.args else ""
    msg = f"🔄 Iniciando ciclo de aprendizado{f' para nicho: {niche}' if niche else ''}...\n"
    msg += "Isso pode levar alguns segundos."
    await update.message.reply_text(msg)

    try:
        # Usa o pipeline LEARN do orquestrador
        from core.orchestrator import orchestrator, PipelineMode, TaskContext
        task_ctx = TaskContext(
            original_prompt=f"aprender {niche}".strip(),
            mode=PipelineMode.LEARN,
            niche=niche,
            language="pt-BR",
        )
        result = await orchestrator._run_learning(task_ctx)

        steps_text = []
        for step in result.get("steps", []):
            status = step.get("status", "?")
            emoji = "✅" if status == "ok" else ("⏭" if status == "skipped" else "❌")
            step_name = step.get("step", "")
            detail = ""
            if step_name == "scraping" and status == "ok":
                detail = f" ({step.get('new_items', 0)} novos itens)"
            elif step_name == "dna_extraction" and status == "ok":
                detail = f" ({step.get('dnas_created', 0)} DNAs criados)"
            elif step.get("reason"):
                detail = f" — {step['reason']}"
            steps_text.append(f"{emoji} {step_name}{detail}")

        stats = result.get("database_stats", {})
        stats_text = (
            f"\n📚 *Base de conhecimento:*\n"
            f"• {stats.get('scraped_total', 0)} vídeos coletados\n"
            f"• {stats.get('dna_patterns', 0)} padrões DNA\n"
            f"• {stats.get('performance_feedbacks', 0)} feedbacks de performance"
        ) if stats else ""

        await update.message.reply_text(
            "🧠 *Ciclo de aprendizado concluído*\n\n"
            + "\n".join(steps_text)
            + stats_text,
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Erro no ciclo de aprendizado: {e}")


async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Exibe estatísticas do sistema."""
    try:
        stats = get_scraping_stats()
        history = get_history(limit=5)

        niches_text = "\n".join(
            f"  • {n}: {c} vídeos"
            for n, c in list(stats.get("niches", {}).items())[:5]
        )

        await update.message.reply_text(
            "📊 *STATUS DO SISTEMA*\n\n"
            f"*Banco de dados:*\n"
            f"• {stats['scraped_total']} vídeos scraped\n"
            f"• {stats['scraped_analyzed']} analisados\n"
            f"• {stats['dna_patterns']} padrões DNA\n"
            f"• {stats['performance_feedbacks']} feedbacks\n\n"
            f"*Nichos com dados:*\n{niches_text or '  (nenhum ainda)'}\n\n"
            f"*Últimas gerações:* {len(history)}\n\n"
            "Use /aprender [nicho] para coletar dados novos.",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {e}")


async def cmd_historico(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Lista últimos conteúdos gerados."""
    history = get_history(limit=8)
    if not history:
        await update.message.reply_text("Nenhum conteúdo gerado ainda.")
        return

    lines = ["📋 *Últimas gerações:*\n"]
    for i, item in enumerate(history, 1):
        lines.append(
            f"{i}. [{item.get('mode', '?')}] {item.get('niche', '?')} — "
            f"{item.get('platform', '?')} | {item.get('created_at', '')[:10]}"
        )

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------

def run_bot():
    app = Application.builder().token(config.telegram.bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("criar", handle_message))
    app.add_handler(CommandHandler("full", handle_message))
    app.add_handler(CommandHandler("pesquisar", handle_message))
    app.add_handler(CommandHandler("otimizar", handle_message))
    app.add_handler(CommandHandler("resultado", cmd_resultado))
    app.add_handler(CommandHandler("aprender", cmd_aprender))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("historico", cmd_historico))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot rodando...")
    app.run_polling()


if __name__ == "__main__":
    run_bot()
