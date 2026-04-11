// =====================================================
// AGENTE BLENDER — Geração de renders 3D & animações
// =====================================================
// Pipeline completo:
//   1. Recebe produto do catálogo (via evento ou fila)
//   2. Seleciona template de cena por categoria
//   3. Envia job ao servidor Blender (Docker/cloud)
//   4. Blender executa: modelagem → materiais → iluminação → render
//   5. Output: renders estáticos + animação 360° + explosão de peças
//   6. Notifica Shopify para atualizar imagens do produto
// =====================================================

import { AgenteBase } from '../../core/agente-base.js';

class AgenteBlender extends AgenteBase {
    constructor(config = {}) {
        super({
            id: 'blender',
            nome: 'Agente Blender',
            descricao: 'Gera renders 3D, animações 360° e explosão de peças para produtos do catálogo',
            intervaloMinutos: config.intervaloMinutos || 45
        });

        // === CONFIGURAÇÃO DO SERVIDOR BLENDER ===
        this.serverUrl = config.serverUrl || process.env.BLENDER_SERVER_URL || 'http://localhost:8585';
        this.apiKey = config.apiKey || process.env.BLENDER_API_KEY || null;

        // === CONFIGURAÇÃO DE RENDER ===
        this.renderConfig = {
            // Engine de render
            engine: config.engine || 'CYCLES',          // CYCLES (realista) ou EEVEE (rápido)
            samples: config.samples || 128,              // Amostras (128=rápido, 512=produção)
            resolution: config.resolution || { x: 1920, y: 1920 },  // Quadrado para e-commerce

            // Formato de saída
            imageFormat: 'PNG',
            videoFormat: 'MP4',
            videoCodec: 'H264',
            fps: 30,

            // Qualidade
            denoising: true,
            transparentBackground: true,     // Fundo transparente para fotos de produto
            colorManagement: 'Filmic',       // Melhor para produtos
        };

        // === PALETAS CINEMATOGRÁFICAS ===
        this.cinematicPalettes = [
            'tech_blue', 'energy_orange', 'cyber_purple',
            'matrix_green', 'fire_red', 'ice_white'
        ];

        // === ESTILOS DE CÂMERA CINEMATOGRÁFICA ===
        this.cameraStyles = ['orbit_zoom', 'push_in', 'reveal'];

        // === TIPOS DE OBJETO CINEMATOGRÁFICO ===
        this.cinematicObjects = ['sphere', 'cube', 'torus', 'product'];

        // === TIPOS DE RENDER POR PRODUTO ===
        this.renderTypes = {
            // Foto principal — ângulo 3/4 com iluminação studio
            hero: {
                id: 'hero',
                nome: 'Hero Shot',
                camera: { angle: 'three_quarter', distance: 'medium' },
                lighting: 'studio_3point',
                background: 'gradient_white',
                resolution: { x: 1920, y: 1920 },
                samples: 256
            },
            // Fotos laterais — frente, lado, trás, topo
            multiAngle: {
                id: 'multi_angle',
                nome: 'Multi-Angle',
                angles: ['front', 'right', 'back', 'top'],
                lighting: 'studio_soft',
                background: 'transparent',
                resolution: { x: 1200, y: 1200 },
                samples: 128
            },
            // Animação 360° — turntable
            turntable: {
                id: 'turntable_360',
                nome: 'Turntable 360°',
                frames: 120,      // 4 segundos a 30fps
                lighting: 'studio_3point',
                background: 'gradient_dark',
                resolution: { x: 1080, y: 1080 },
                samples: 64
            },
            // Explosão de peças — mostra componentes internos
            exploded: {
                id: 'exploded_view',
                nome: 'Exploded View',
                animation: true,
                frames: 90,       // 3 segundos
                lighting: 'studio_clean',
                background: 'transparent',
                resolution: { x: 1920, y: 1080 },
                samples: 128
            },
            // Lifestyle — produto em contexto real
            lifestyle: {
                id: 'lifestyle',
                nome: 'Lifestyle Scene',
                camera: { angle: 'perspective', distance: 'scene' },
                lighting: 'environment_hdri',
                background: 'scene',
                resolution: { x: 1920, y: 1080 },
                samples: 256
            },

            // =====================================================
            // CINEMATOGRÁFICOS — Vídeos premium com efeitos avançados
            // =====================================================

            // Desmontagem cinematográfica — objeto se abre revelando camadas internas
            cinematicDisassembly: {
                id: 'cinematic_disassembly',
                nome: 'Desmontagem Cinematográfica',
                cinematic: true,
                frames: 150,           // 5 segundos
                cameraStyle: 'orbit_zoom',
                effects: ['core', 'dust', 'sparks', 'fragments'],
                disassembly: true,
                layers: 4,
                motionBlur: true,
                resolution: { x: 1920, y: 1080 },
                samples: 200
            },
            // Push-in dramático — câmera avança com energia no centro
            cinematicPushIn: {
                id: 'cinematic_push_in',
                nome: 'Push-In Dramático',
                cinematic: true,
                frames: 120,           // 4 segundos
                cameraStyle: 'push_in',
                effects: ['core', 'dust'],
                disassembly: false,
                layers: 1,
                motionBlur: true,
                resolution: { x: 1920, y: 1080 },
                samples: 200
            },
            // Reveal — começa de perto (blur), afasta revelando o produto
            cinematicReveal: {
                id: 'cinematic_reveal',
                nome: 'Reveal Cinematográfico',
                cinematic: true,
                frames: 120,
                cameraStyle: 'reveal',
                effects: ['core', 'dust', 'sparks'],
                disassembly: true,
                layers: 3,
                motionBlur: true,
                resolution: { x: 1920, y: 1080 },
                samples: 200
            },
            // Orbit showcase — rotação suave com efeitos
            cinematicOrbit: {
                id: 'cinematic_orbit',
                nome: 'Orbit Showcase',
                cinematic: true,
                frames: 180,           // 6 segundos
                cameraStyle: 'orbit_zoom',
                effects: ['core', 'dust'],
                disassembly: false,
                layers: 2,
                motionBlur: false,
                resolution: { x: 1920, y: 1080 },
                samples: 150
            }
        };

        // === FILA DE JOBS ===
        this.jobQueue = [];
        this.activeJobs = new Map();
        this.maxConcurrentJobs = config.maxConcurrentJobs || 2;

        // === ESTATÍSTICAS ===
        this.stats = {
            totalRendersGerados: 0,
            totalAnimacoesGeradas: 0,
            totalJobsConcluidos: 0,
            totalJobsFalhados: 0,
            tempoMedioRenderMs: 0,
            ultimoRender: null
        };
    }

    // =====================================================
    // TAREFA PRINCIPAL — Executada a cada ciclo
    // =====================================================
    async _tarefa() {
        const acoes = [];
        let dados = {};

        try {
            // 1. Verificar saúde do servidor Blender
            const serverOk = await this._verificarServidor();
            if (!serverOk) {
                return {
                    sucesso: false,
                    acoes: ['servidor_indisponivel'],
                    dados: { serverUrl: this.serverUrl },
                    mensagem: `Servidor Blender indisponível em ${this.serverUrl}`
                };
            }
            acoes.push('servidor_verificado');

            // 2. Buscar produtos que precisam de renders
            const produtosPendentes = await this._buscarProdutosSemRender();
            dados.produtosPendentes = produtosPendentes.length;

            // 3. Processar fila de jobs existentes
            const jobsConcluidos = await this._processarJobsAtivos();
            if (jobsConcluidos.length > 0) {
                acoes.push(`${jobsConcluidos.length}_jobs_concluidos`);
                dados.jobsConcluidos = jobsConcluidos;
            }

            // 4. Criar novos jobs para produtos pendentes
            const novosJobs = await this._criarJobsParaProdutos(produtosPendentes);
            if (novosJobs.length > 0) {
                acoes.push(`${novosJobs.length}_jobs_criados`);
                dados.novosJobs = novosJobs.map(j => j.produtoNome);
            }

            // 5. Submeter jobs ao servidor
            const jobsSubmetidos = await this._submeterJobs();
            if (jobsSubmetidos > 0) {
                acoes.push(`${jobsSubmetidos}_jobs_submetidos`);
            }

            // 6. Notificar renders prontos para Shopify
            for (const job of jobsConcluidos) {
                this.notificar('renders_prontos', {
                    produtoId: job.produtoId,
                    shopifyProductId: job.shopifyProductId,
                    renders: job.renders,
                    animacoes: job.animacoes
                });
            }

            return {
                sucesso: true,
                acoes,
                dados: {
                    ...dados,
                    filaAtual: this.jobQueue.length,
                    jobsAtivos: this.activeJobs.size,
                    stats: this.stats
                },
                mensagem: `Ciclo completo: ${acoes.length} ações executadas`
            };

        } catch (erro) {
            await this._log('erro', `Erro no ciclo: ${erro.message}`);
            return {
                sucesso: false,
                acoes,
                dados,
                mensagem: `Erro: ${erro.message}`
            };
        }
    }

    // =====================================================
    // VERIFICAÇÃO DO SERVIDOR
    // =====================================================
    async _verificarServidor() {
        try {
            const response = await this.fetchComRetry(`${this.serverUrl}/api/health`, {}, 1);
            if (response?.status === 'ok') {
                await this._log('info', `Servidor Blender OK: ${response.blenderVersion || 'desconhecida'}`);
                return true;
            }
            return false;
        } catch (erro) {
            // Modo demo — servidor não disponível, simular
            await this._log('aviso', `Servidor Blender não disponível — modo DEMO ativado`);
            this._modoDemo = true;
            return true; // Continuar em modo demo
        }
    }

    // =====================================================
    // BUSCAR PRODUTOS QUE PRECISAM DE RENDER
    // =====================================================
    async _buscarProdutosSemRender() {
        if (!this.db) return [];

        try {
            // Buscar produtos ativos sem renders 3D
            const produtos = await this.db.getProdutos({ status: 'ativo' });

            // Filtrar os que não têm renders ou estão desatualizados
            const semRender = produtos.filter(p => {
                const metadata = p.metadata ? JSON.parse(p.metadata) : {};
                return !metadata.blender_renders || metadata.blender_renders_outdated;
            });

            await this._log('info', `${semRender.length} produtos sem renders 3D`);
            return semRender.slice(0, 5); // Processar max 5 por ciclo

        } catch (erro) {
            await this._log('aviso', `Erro ao buscar produtos: ${erro.message}`);
            return [];
        }
    }

    // =====================================================
    // CRIAR JOBS PARA PRODUTOS
    // =====================================================
    async _criarJobsParaProdutos(produtos) {
        const novosJobs = [];

        for (const produto of produtos) {
            const template = this._selecionarTemplate(produto);
            const rendersPedidos = this._definirRendersPorCategoria(produto);

            const job = {
                id: `job_${Date.now()}_${produto.id}`,
                produtoId: produto.id,
                produtoNome: produto.nome,
                shopifyProductId: produto.shopify_product_id,
                sku: produto.sku,
                categoria: produto.categoria,
                template: template,
                renders: rendersPedidos,
                status: 'pendente',
                criadoEm: new Date().toISOString(),
                tentativas: 0,
                maxTentativas: 3,
                resultado: null
            };

            this.jobQueue.push(job);
            novosJobs.push(job);

            await this._log('info', `Job criado: ${job.id} — ${produto.nome} (${rendersPedidos.length} renders)`);
        }

        return novosJobs;
    }

    // =====================================================
    // SELECIONAR TEMPLATE DE CENA POR CATEGORIA
    // =====================================================
    _selecionarTemplate(produto) {
        const categoria = (produto.categoria || '').toLowerCase();

        // Templates mapeados por categoria de produto
        const templateMap = {
            // === ELETRÔNICOS ===
            'smart_plug': 'electronics_small',
            'carregador': 'electronics_small',
            'cabo': 'electronics_small',
            'adaptador': 'electronics_small',
            'hub_usb': 'electronics_small',

            // === ÁUDIO ===
            'fone': 'audio_wearable',
            'earbuds': 'audio_wearable',
            'speaker': 'audio_speaker',
            'caixa_som': 'audio_speaker',

            // === ILUMINAÇÃO ===
            'led': 'lighting_strip',
            'led_strip': 'lighting_strip',
            'lampada': 'lighting_bulb',
            'luminaria': 'lighting_desk',

            // === WEARABLES ===
            'smartwatch': 'wearable_watch',
            'pulseira': 'wearable_band',
            'rastreador': 'wearable_tracker',

            // === CASA INTELIGENTE ===
            'camera': 'smarthome_camera',
            'sensor': 'smarthome_sensor',
            'tomada': 'smarthome_plug',
            'interruptor': 'smarthome_switch',

            // === GAMING ===
            'controle': 'gaming_controller',
            'headset': 'gaming_headset',
            'teclado': 'gaming_keyboard',
            'mouse': 'gaming_mouse',

            // === ACESSÓRIOS CELULAR ===
            'capinha': 'phone_case',
            'suporte': 'phone_holder',
            'pelicula': 'phone_screen',

            // === COZINHA/GADGETS ===
            'cozinha': 'kitchen_gadget',
            'gadget': 'generic_gadget'
        };

        // Tentar match direto
        if (templateMap[categoria]) {
            return templateMap[categoria];
        }

        // Match parcial por keywords
        for (const [key, template] of Object.entries(templateMap)) {
            if (categoria.includes(key) || (produto.nome || '').toLowerCase().includes(key)) {
                return template;
            }
        }

        // Fallback genérico
        return 'generic_product';
    }

    // =====================================================
    // DEFINIR RENDERS POR CATEGORIA
    // =====================================================
    _definirRendersPorCategoria(produto) {
        const categoria = (produto.categoria || '').toLowerCase();
        const renders = [];

        // TODOS os produtos recebem: hero + multi-angle
        renders.push({ ...this.renderTypes.hero });
        renders.push({ ...this.renderTypes.multiAngle });

        // Eletrônicos e smart home — explosão de peças
        const temExplosao = ['smart_plug', 'carregador', 'fone', 'earbuds', 'speaker',
            'smartwatch', 'camera', 'sensor', 'controle', 'headset', 'teclado', 'mouse'];
        if (temExplosao.some(k => categoria.includes(k))) {
            renders.push({ ...this.renderTypes.exploded });
        }

        // Wearables, gadgets, áudio — turntable 360°
        const temTurntable = ['fone', 'earbuds', 'speaker', 'smartwatch', 'pulseira',
            'controle', 'headset', 'cozinha', 'gadget', 'capinha'];
        if (temTurntable.some(k => categoria.includes(k))) {
            renders.push({ ...this.renderTypes.turntable });
        }

        // Smart home, iluminação — lifestyle shot
        const temLifestyle = ['led', 'lampada', 'luminaria', 'camera', 'sensor',
            'tomada', 'interruptor', 'cozinha'];
        if (temLifestyle.some(k => categoria.includes(k))) {
            renders.push({ ...this.renderTypes.lifestyle });
        }

        return renders;
    }

    // =====================================================
    // SUBMETER JOBS AO SERVIDOR BLENDER
    // =====================================================
    async _submeterJobs() {
        let submetidos = 0;

        while (this.jobQueue.length > 0 && this.activeJobs.size < this.maxConcurrentJobs) {
            const job = this.jobQueue.shift();

            try {
                // Detectar tipo de job
                const isCinematic = job.tipo === 'cinematic';

                if (this._modoDemo) {
                    // MODO DEMO — simular submissão
                    const demoResult = isCinematic
                        ? this._simularJobCinematico(job)
                        : this._simularJob(job);
                    this.activeJobs.set(job.id, { ...job, status: 'processando', demoResult });
                } else {
                    // MODO PRODUÇÃO — enviar ao servidor
                    const payload = isCinematic ? {
                        jobId: job.id,
                        product: {
                            id: job.produtoId,
                            name: job.produtoNome,
                            sku: job.sku || job.produtoId,
                            category: job.categoria
                        },
                        template: job.template || 'cinematic',
                        renders: [{
                            id: 'cinematic',
                            type: 'cinematic',
                            cinematic: job.cinematic,
                            outputFolder: job.sku || job.id
                        }],
                        config: { ...this.renderConfig, cinematic: true }
                    } : {
                        jobId: job.id,
                        product: {
                            id: job.produtoId,
                            name: job.produtoNome,
                            sku: job.sku,
                            category: job.categoria
                        },
                        template: job.template,
                        renders: job.renders,
                        config: this.renderConfig
                    };

                    const response = await this.fetchComRetry(`${this.serverUrl}/api/jobs`, {
                        method: 'POST',
                        body: JSON.stringify(payload),
                        headers: {
                            'Content-Type': 'application/json',
                            ...(this.apiKey ? { 'Authorization': `Bearer ${this.apiKey}` } : {})
                        }
                    });

                    this.activeJobs.set(job.id, {
                        ...job,
                        status: 'processando',
                        serverJobId: response.jobId,
                        submetidoEm: new Date().toISOString()
                    });
                }

                submetidos++;
                await this._log('info', `Job submetido: ${job.id} — ${job.produtoNome}`);

            } catch (erro) {
                job.tentativas++;
                if (job.tentativas < job.maxTentativas) {
                    this.jobQueue.push(job); // Recolocar na fila
                    await this._log('aviso', `Job ${job.id} falhou (tentativa ${job.tentativas}) — recolocado na fila`);
                } else {
                    await this._log('erro', `Job ${job.id} descartado após ${job.maxTentativas} tentativas`);
                    this.stats.totalJobsFalhados++;
                }
            }
        }

        return submetidos;
    }

    // =====================================================
    // PROCESSAR JOBS ATIVOS (verificar conclusão)
    // =====================================================
    async _processarJobsAtivos() {
        const concluidos = [];

        for (const [jobId, job] of this.activeJobs) {
            try {
                let resultado;

                if (this._modoDemo) {
                    // DEMO: job "conclui" imediatamente
                    resultado = job.demoResult;
                } else {
                    // PRODUÇÃO: verificar status no servidor
                    resultado = await this.fetchComRetry(
                        `${this.serverUrl}/api/jobs/${job.serverJobId}`,
                        {}, 1
                    );
                }

                if (resultado.status === 'completed') {
                    // Job concluído com sucesso
                    const jobConcluido = {
                        ...job,
                        status: 'concluido',
                        renders: resultado.renders || [],
                        animacoes: resultado.animations || [],
                        concluidoEm: new Date().toISOString(),
                        tempoMs: resultado.renderTimeMs || 0
                    };

                    concluidos.push(jobConcluido);
                    this.activeJobs.delete(jobId);

                    // Atualizar stats
                    this.stats.totalJobsConcluidos++;
                    this.stats.totalRendersGerados += (resultado.renders || []).length;
                    this.stats.totalAnimacoesGeradas += (resultado.animations || []).length;
                    this.stats.ultimoRender = new Date().toISOString();

                    // Atualizar tempo médio
                    const total = this.stats.totalJobsConcluidos;
                    this.stats.tempoMedioRenderMs = Math.round(
                        (this.stats.tempoMedioRenderMs * (total - 1) + (resultado.renderTimeMs || 0)) / total
                    );

                    await this._log('info', `✅ Job concluído: ${jobId} — ${resultado.renders?.length || 0} renders, ${resultado.animations?.length || 0} animações`);

                    // Salvar metadados no produto no banco
                    await this._salvarRendersNoProduto(job.produtoId, resultado);

                } else if (resultado.status === 'failed') {
                    await this._log('erro', `❌ Job falhou no servidor: ${jobId} — ${resultado.error}`);
                    this.activeJobs.delete(jobId);
                    this.stats.totalJobsFalhados++;
                }
                // Se 'processing', continua esperando

            } catch (erro) {
                await this._log('aviso', `Erro ao verificar job ${jobId}: ${erro.message}`);
            }
        }

        return concluidos;
    }

    // =====================================================
    // SALVAR REFERÊNCIAS DOS RENDERS NO BANCO
    // =====================================================
    async _salvarRendersNoProduto(produtoId, resultado) {
        if (!this.db) return;

        try {
            const produto = (await this.db.getProdutos({})).find(p => p.id === produtoId);
            if (!produto) return;

            const metadata = produto.metadata ? JSON.parse(produto.metadata) : {};
            metadata.blender_renders = {
                geradoEm: new Date().toISOString(),
                renders: (resultado.renders || []).map(r => ({
                    tipo: r.type,
                    url: r.url,
                    resolucao: r.resolution,
                    tamanho: r.fileSize
                })),
                animacoes: (resultado.animations || []).map(a => ({
                    tipo: a.type,
                    url: a.url,
                    duracao: a.duration,
                    fps: a.fps,
                    tamanho: a.fileSize
                })),
                blender_renders_outdated: false
            };

            // Atualizar produto com metadados de render
            await this.db.run(
                `UPDATE produtos SET metadata = ? WHERE id = ?`,
                [JSON.stringify(metadata), produtoId]
            );

        } catch (erro) {
            await this._log('erro', `Erro ao salvar renders do produto ${produtoId}: ${erro.message}`);
        }
    }

    // =====================================================
    // SIMULAÇÃO (MODO DEMO)
    // =====================================================
    _simularJob(job) {
        const baseUrl = `/output/${job.sku || job.produtoId}`;

        const renders = job.renders
            .filter(r => !r.animation && r.id !== 'turntable_360' && r.id !== 'exploded_view')
            .flatMap(r => {
                if (r.id === 'multi_angle') {
                    return (r.angles || ['front', 'right', 'back', 'top']).map(angle => ({
                        type: `multi_angle_${angle}`,
                        url: `${baseUrl}/${r.id}_${angle}.png`,
                        resolution: r.resolution || this.renderConfig.resolution,
                        fileSize: Math.round(Math.random() * 2000000 + 500000) // 0.5-2.5MB
                    }));
                }
                return [{
                    type: r.id,
                    url: `${baseUrl}/${r.id}.png`,
                    resolution: r.resolution || this.renderConfig.resolution,
                    fileSize: Math.round(Math.random() * 3000000 + 800000) // 0.8-3.8MB
                }];
            });

        const animations = job.renders
            .filter(r => r.animation || r.id === 'turntable_360' || r.id === 'exploded_view')
            .map(r => ({
                type: r.id,
                url: `${baseUrl}/${r.id}.mp4`,
                duration: (r.frames || 120) / (this.renderConfig.fps || 30),
                fps: this.renderConfig.fps || 30,
                fileSize: Math.round(Math.random() * 15000000 + 5000000) // 5-20MB
            }));

        return {
            status: 'completed',
            renders,
            animations,
            renderTimeMs: Math.round(Math.random() * 120000 + 30000), // 30s-150s
            engine: this.renderConfig.engine,
            template: job.template
        };
    }

    // =====================================================
    // SIMULAÇÃO CINEMATOGRÁFICA (MODO DEMO)
    // =====================================================
    _simularJobCinematico(job) {
        const cin = job.cinematic || {};
        const baseUrl = `/output/${job.sku || job.id}`;
        const frames = cin.frames || 120;
        const fps = this.renderConfig.fps || 30;

        const renders = [
            {
                type: 'cinematic_thumbnail',
                url: `${baseUrl}/cinematic_thumbnail.png`,
                resolution: cin.resolution || { x: 1920, y: 1080 },
                fileSize: Math.round(Math.random() * 3000000 + 1000000)
            },
            ...[1, Math.floor(frames / 4), Math.floor(frames / 2), Math.floor(frames * 0.75)].map(kf => ({
                type: `keyframe_${String(kf).padStart(4, '0')}`,
                url: `${baseUrl}/keyframe_${String(kf).padStart(4, '0')}.png`,
                resolution: cin.resolution || { x: 1920, y: 1080 },
                fileSize: Math.round(Math.random() * 2500000 + 800000)
            }))
        ];

        const animations = [{
            type: `cinematic_${cin.cameraStyle || 'orbit_zoom'}`,
            url: `${baseUrl}/cinematic_video.mp4`,
            duration: frames / fps,
            fps: fps,
            palette: cin.palette || 'tech_blue',
            objectType: cin.objectType || 'sphere',
            effects: cin.effects || [],
            disassembly: cin.disassembly || false,
            fileSize: Math.round(Math.random() * 30000000 + 10000000)
        }];

        return {
            status: 'completed',
            renders,
            animations,
            renderTimeMs: Math.round(Math.random() * 300000 + 60000), // 1-6 min
            engine: 'CYCLES',
            type: 'cinematic',
            palette: cin.palette,
            cameraStyle: cin.cameraStyle
        };
    }

    // =====================================================
    // MÉTODOS PÚBLICOS — Chamados por outros agentes/API
    // =====================================================

    /**
     * Solicitar render de um produto específico
     * @param {Object} produto — {id, nome, sku, categoria, shopify_product_id}
     * @param {string[]} tipos — ['hero', 'multiAngle', 'turntable', 'exploded', 'lifestyle']
     */
    async solicitarRender(produto, tipos = ['hero', 'multiAngle']) {
        const renders = tipos
            .map(t => this.renderTypes[t])
            .filter(Boolean);

        if (renders.length === 0) {
            await this._log('aviso', `Nenhum tipo de render válido para: ${tipos.join(', ')}`);
            return null;
        }

        const job = {
            id: `job_${Date.now()}_${produto.id}`,
            produtoId: produto.id,
            produtoNome: produto.nome || produto.name,
            shopifyProductId: produto.shopify_product_id,
            sku: produto.sku,
            categoria: produto.categoria || produto.category,
            template: this._selecionarTemplate(produto),
            renders,
            status: 'pendente',
            criadoEm: new Date().toISOString(),
            tentativas: 0,
            maxTentativas: 3
        };

        this.jobQueue.push(job);
        await this._log('info', `Render solicitado: ${job.id} — ${produto.nome} (${renders.length} tipos)`);

        // Tentar submeter imediatamente se há slots
        if (this.activeJobs.size < this.maxConcurrentJobs) {
            await this._submeterJobs();
        }

        return job.id;
    }

    /**
     * Solicitar render completo (todos os tipos relevantes para a categoria)
     */
    async solicitarRenderCompleto(produto) {
        const renders = this._definirRendersPorCategoria(produto);
        const tipos = renders.map(r => r.id);
        return this.solicitarRender(produto, tipos);
    }

    /**
     * Obter status de um job
     */
    getJobStatus(jobId) {
        // Verificar ativos
        if (this.activeJobs.has(jobId)) {
            return this.activeJobs.get(jobId);
        }
        // Verificar fila
        const naFila = this.jobQueue.find(j => j.id === jobId);
        if (naFila) return naFila;
        return null;
    }

    /**
     * Obter estatísticas do agente
     */
    getStats() {
        return {
            ...this.stats,
            filaAtual: this.jobQueue.length,
            jobsAtivos: this.activeJobs.size,
            renderConfig: {
                engine: this.renderConfig.engine,
                samples: this.renderConfig.samples,
                resolution: this.renderConfig.resolution
            },
            modoDemo: !!this._modoDemo
        };
    }

    /**
     * Atualizar configuração de render
     */
    atualizarConfig(novaConfig) {
        Object.assign(this.renderConfig, novaConfig);
        this._log('info', `Config de render atualizada: ${JSON.stringify(novaConfig)}`);
    }

    // =====================================================
    // MÉTODOS CINEMATOGRÁFICOS — Conteúdo premium
    // =====================================================

    /**
     * Gerar vídeo cinematográfico de um produto
     * @param {Object} produto — {id, nome, sku, categoria}
     * @param {Object} opcoes — configurações do vídeo cinematográfico
     *   - palette: 'tech_blue' | 'energy_orange' | 'cyber_purple' | 'matrix_green' | 'fire_red' | 'ice_white'
     *   - cameraStyle: 'orbit_zoom' | 'push_in' | 'reveal'
     *   - effects: ['core', 'dust', 'sparks', 'fragments']
     *   - disassembly: true/false (explodir peças)
     *   - layers: 1-5 (camadas internas)
     *   - frames: número de frames (120 = 4s a 30fps)
     */
    async gerarVideoCinematico(produto, opcoes = {}) {
        const defaults = {
            palette: 'tech_blue',
            cameraStyle: 'orbit_zoom',
            effects: ['core', 'dust', 'sparks'],
            disassembly: true,
            layers: 4,
            frames: 150,
            motionBlur: true,
            objectType: 'product',
            samples: 200,
            resolution: { x: 1920, y: 1080 }
        };

        const config = { ...defaults, ...opcoes };

        const job = {
            id: `cin_${Date.now()}_${produto.id || produto.sku}`,
            produtoId: produto.id,
            produtoNome: produto.nome || produto.name,
            shopifyProductId: produto.shopify_product_id,
            sku: produto.sku,
            categoria: produto.categoria || produto.category,
            template: this._selecionarTemplate(produto),
            tipo: 'cinematic',
            cinematic: {
                palette: config.palette,
                cameraStyle: config.cameraStyle,
                effects: config.effects,
                disassembly: config.disassembly,
                layers: config.layers,
                frames: config.frames,
                motionBlur: config.motionBlur,
                objectType: config.objectType,
                productTemplate: this._selecionarTemplate(produto),
                productInfo: {
                    id: produto.id,
                    name: produto.nome,
                    sku: produto.sku,
                    category: produto.categoria
                }
            },
            renders: [], // Cinematográfico usa pipeline diferente
            status: 'pendente',
            criadoEm: new Date().toISOString(),
            tentativas: 0,
            maxTentativas: 3
        };

        this.jobQueue.push(job);
        await this._log('info', `🎬 Vídeo cinematográfico solicitado: ${job.id} — ${produto.nome} [${config.palette}/${config.cameraStyle}]`);

        if (this.activeJobs.size < this.maxConcurrentJobs) {
            await this._submeterJobs();
        }

        return job.id;
    }

    /**
     * Gerar vídeo cinematográfico com objeto abstrato (não produto)
     * Para conteúdo viral, branding, redes sociais
     * @param {string} objectType — 'sphere' | 'cube' | 'torus'
     * @param {Object} opcoes — mesmas opções de gerarVideoCinematico
     */
    async gerarConteudoCinematico(objectType = 'sphere', opcoes = {}) {
        const defaults = {
            palette: 'tech_blue',
            cameraStyle: 'orbit_zoom',
            effects: ['core', 'dust', 'sparks'],
            disassembly: true,
            layers: 4,
            frames: 150,
            motionBlur: true,
            samples: 200,
            resolution: { x: 1920, y: 1080 }
        };

        const config = { ...defaults, ...opcoes };

        const job = {
            id: `cin_${Date.now()}_${objectType}`,
            produtoId: null,
            produtoNome: `Cinematic ${objectType}`,
            shopifyProductId: null,
            sku: `cinematic_${objectType}`,
            categoria: 'cinematic',
            template: 'cinematic',
            tipo: 'cinematic',
            cinematic: {
                palette: config.palette,
                cameraStyle: config.cameraStyle,
                effects: config.effects,
                disassembly: config.disassembly,
                layers: config.layers,
                frames: config.frames,
                motionBlur: config.motionBlur,
                objectType: objectType,
            },
            renders: [],
            status: 'pendente',
            criadoEm: new Date().toISOString(),
            tentativas: 0,
            maxTentativas: 3
        };

        this.jobQueue.push(job);
        await this._log('info', `🎬 Conteúdo cinematográfico: ${job.id} — ${objectType} [${config.palette}/${config.cameraStyle}]`);

        if (this.activeJobs.size < this.maxConcurrentJobs) {
            await this._submeterJobs();
        }

        return job.id;
    }

    /**
     * Gerar batch de conteúdo — várias combinações de cor/objeto/câmera
     * 1 template = N vídeos (troca cor, objeto, estilo de câmera)
     */
    async gerarBatchCinematico(configs = []) {
        if (configs.length === 0) {
            // Gerar combinações automáticas
            configs = this._gerarCombinacoesAutomaticas();
        }

        const jobIds = [];
        for (const config of configs) {
            const jobId = await this.gerarConteudoCinematico(
                config.objectType || 'sphere',
                config
            );
            jobIds.push(jobId);
        }

        await this._log('info', `🎬 Batch cinematográfico: ${jobIds.length} vídeos enfileirados`);
        return jobIds;
    }

    /**
     * Gerar combinações automáticas para batch
     * @param {number} maxCombos — máximo de combinações
     */
    _gerarCombinacoesAutomaticas(maxCombos = 6) {
        const combos = [];
        const objects = ['sphere', 'cube', 'torus'];
        const palettes = ['tech_blue', 'energy_orange', 'cyber_purple'];
        const cameras = ['orbit_zoom', 'push_in', 'reveal'];

        for (const obj of objects) {
            for (const palette of palettes) {
                const camera = cameras[Math.floor(Math.random() * cameras.length)];
                combos.push({
                    objectType: obj,
                    palette: palette,
                    cameraStyle: camera,
                    disassembly: true,
                    layers: obj === 'sphere' ? 4 : 3,
                    effects: ['core', 'dust', 'sparks']
                });
                if (combos.length >= maxCombos) return combos;
            }
        }
        return combos;
    }

    /**
     * Preview rápido com EEVEE — gera em segundos para testar composição
     * @param {Object} produto — {id, nome, sku, categoria}
     * @param {Object} opcoes — mesmas opções de cinematic, mas com override EEVEE
     */
    async gerarPreview(produto, opcoes = {}) {
        const previewOpcoes = {
            ...opcoes,
            samples: 32,                          // EEVEE precisa de poucos samples
            resolution: { x: 960, y: 540 },       // Metade da resolução
            frames: Math.min(opcoes.frames || 60, 60),  // Max 60 frames (2s)
            engine: 'EEVEE',                       // Engine rápida
            motionBlur: false,                     // Sem motion blur para velocidade
            bloom: 0.5,                            // Bloom reduzido
            preview: true                          // Flag para server
        };

        await this._log('info', `⚡ Preview rápido EEVEE: ${produto.nome || produto.name}`);
        return this.gerarVideoCinematico(produto, previewOpcoes);
    }

    /**
     * Listar paletas cinematográficas disponíveis
     */
    getPaletasDisponiveis() {
        return {
            tech_blue: 'Azul elétrico tech — o clássico sci-fi',
            energy_orange: 'Laranja energia — quente e dinâmico',
            cyber_purple: 'Roxo cyber — futurista e misterioso',
            matrix_green: 'Verde matrix — digital e hacker',
            fire_red: 'Vermelho fogo — intenso e poderoso',
            ice_white: 'Branco gelo — clean e premium'
        };
    }

    /**
     * Listar templates disponíveis
     */
    getTemplatesDisponiveis() {
        return {
            electronics_small: 'Eletrônicos pequenos (plugs, cabos, carregadores)',
            audio_wearable: 'Fones e earbuds',
            audio_speaker: 'Caixas de som e speakers',
            lighting_strip: 'Fitas LED',
            lighting_bulb: 'Lâmpadas inteligentes',
            lighting_desk: 'Luminárias de mesa',
            wearable_watch: 'Smartwatches',
            wearable_band: 'Pulseiras fitness',
            wearable_tracker: 'Rastreadores',
            smarthome_camera: 'Câmeras de segurança',
            smarthome_sensor: 'Sensores IoT',
            smarthome_plug: 'Tomadas inteligentes',
            smarthome_switch: 'Interruptores smart',
            gaming_controller: 'Controles de jogo',
            gaming_headset: 'Headsets gamer',
            gaming_keyboard: 'Teclados mecânicos',
            gaming_mouse: 'Mouses gamer',
            phone_case: 'Capinhas de celular',
            phone_holder: 'Suportes para celular',
            phone_screen: 'Películas de proteção',
            kitchen_gadget: 'Gadgets de cozinha',
            generic_gadget: 'Gadgets genéricos',
            generic_product: 'Produto genérico (fallback)'
        };
    }
}

export { AgenteBlender, };

// Re-exportar constantes úteis
export const CINEMATIC_PALETTES = [
    'tech_blue', 'energy_orange', 'cyber_purple',
    'matrix_green', 'fire_red', 'ice_white'
];

export const CAMERA_STYLES = ['orbit_zoom', 'push_in', 'reveal'];

export const CINEMATIC_OBJECTS = ['sphere', 'cube', 'torus', 'product'];
