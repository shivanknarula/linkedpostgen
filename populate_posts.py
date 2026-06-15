import csv
import os

def populate_database():
    csv_file = "robotics_posts.csv"
    
    # 50 Global Posts
    global_posts = [
        {
            "url": "https://www.linkedin.com/in/brettadcock/recent-activity/all/",
            "date": "2026-06-12",
            "score": "10",
            "reasoning": "Major product announcement from a leading humanoid robotics company. Thought leadership on hardware design and scalability.",
            "comment": "The Figure 02 hardware iteration looks incredibly polished, Brett. The integrated routing and custom actuation are clean. Are you targeting a specific sub-assembly task first in the BMW trials, or is the initial focus on general material handling?",
            "likes": "4520",
            "comments": "312",
            "text": "Figure 02 is officially here. This is our second-generation humanoid robot. We have rebuilt everything from the ground up: new custom actuators, higher battery density, integrated wiring harness, and advanced vision systems. We are already deploying them at BMW's Spartanburg plant. Humanoid robots are entering the production line.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/yann-lecun/recent-activity/all/",
            "date": "2026-06-11",
            "score": "9",
            "reasoning": "Deep theoretical discussion by a Turing Award winner on the future of AI architectures and world models.",
            "comment": "Autoregressive LLMs are indeed hitting scaling walls for true reasoning, Yann. A V-JEPA style approach for world models seems essential for physical AI. How do you view the trade-off in sample efficiency when learning multi-modal representations for robotic planning?",
            "likes": "6810",
            "comments": "498",
            "text": "Autoregessive LLMs cannot achieve true AGI because they lack a world model and are prone to hallucination. We must move toward Joint Embedding Predictive Architectures (JEPA) that predict representations in abstract space rather than predicting every single pixel or token. This is the only path to autonomous agents that can plan and reason.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/demishassabis/recent-activity/all/",
            "date": "2026-06-10",
            "score": "10",
            "reasoning": "Major scientific milestone announcement. AlphaFold 3 open source code release. High global significance.",
            "comment": "An incredible contribution to open science, Demis. The implications for custom drug discovery and bio-robotics are vast. How is DeepMind planning to integrate these structural predictions with downstream molecular dynamics simulations?",
            "likes": "8900",
            "comments": "560",
            "text": "We are proud to fully open-source the code and model weights for AlphaFold 3. It can now predict structures and interactions for proteins, DNA, RNA, and chemical compounds. We hope this empowers researchers worldwide to accelerate drug discovery and biology studies.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/andrewng/recent-activity/all/",
            "date": "2026-06-09",
            "score": "9",
            "reasoning": "Industry leader discussing AI agentic workflows, iterative planning, and execution frameworks. High authority value.",
            "comment": "Iterative agentic workflows are indeed showing higher gains than raw model scaling, Andrew. By breaking tasks down into planning, code generation, and self-reflection, we get far more robust outputs. What evaluation frameworks do you recommend to benchmark agent drift in long-horizon tasks?",
            "likes": "3920",
            "comments": "280",
            "text": "Many people focus on zero-shot LLM prompts, but the real power lies in Agentic Workflows. By allowing LLMs to plan, call tools, write code, run it, and iterate on errors, we can get GPT-3.5-level models to outperform GPT-4 on coding benchmarks. Focus on the workflow, not just the model.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/fei-fei-li-66779313/recent-activity/all/",
            "date": "2026-06-08",
            "score": "10",
            "reasoning": "Announcement of a new stealth AI startup focused on spatial intelligence and physical AI by a pioneer.",
            "comment": "Spatial intelligence is indeed the missing link between digital LLMs and the physical world, Fei-Fei. Building world models that understand geometry and physics will accelerate humanoid navigation. Are you focusing on generative 3D simulation or zero-shot edge control first?",
            "likes": "7200",
            "comments": "410",
            "text": "I am excited to announce World Labs. We are building spatial intelligence models that understand the 3D physical world: geometry, physics, and dynamics. If we want AI to act in the real world, it needs to see and interact in three dimensions. We look forward to sharing our research soon.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/andrej-karpathy/recent-activity/all/",
            "date": "2026-06-07",
            "score": "9",
            "reasoning": "Highly technical post discussing LLM architecture as an operating system kernel. Prompts deep technical conversation.",
            "comment": "The LLM-as-OS model is a powerful abstraction, Andrej. Memory hierarchy (context window as RAM, vector DB as disk) makes perfect sense. Do you see the planning/reasoning loop becoming a hardware-accelerated instruction, or will it remain in the software orchestration layer?",
            "likes": "12000",
            "comments": "890",
            "text": "Think of an LLM not as a chatbot, but as the kernel of a new operating system (the LLM OS). It coordinates tools, memory (context window and vector search), and compute (code execution). The future is about building this operating system stack, making it efficient, secure, and fast.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/ilyasutskever/recent-activity/all/",
            "date": "2026-06-06",
            "score": "10",
            "reasoning": "Announcement of a new safety-focused AI research lab (SSI) by OpenAI co-founder. High global attention.",
            "comment": "A critical mission, Ilya. Focusing solely on safe superintelligence with a dedicated lab insulated from short-term commercial pressures is a bold and necessary move. How will you benchmark alignment when model capabilities start outstripping human evaluators?",
            "likes": "15400",
            "comments": "1120",
            "text": "We are starting Safe Superintelligence Inc. (SSI). Our singular focus is building a safe and powerful superintelligence. We have one goal, one product, and one team, completely insulated from short-term commercial pressures. This is the most important problem of our time.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/samaltman/recent-activity/all/",
            "date": "2026-06-05",
            "score": "9",
            "reasoning": "High-profile post by OpenAI CEO on AGI timeline, compute scaling, and societal impacts. High visibility.",
            "comment": "Compute scaling laws continue to hold, Sam. The challenge is energy generation for these datacenters. Are you betting on nuclear fusion/fission integration to power the next decade's training clusters, or are we looking at decentralized architectures?",
            "likes": "9430",
            "comments": "720",
            "text": "AGI is coming, and it will happen much faster than people realize. The bottleneck right now is compute infrastructure: energy, datacenters, and silicon. The companies and nations that build the energy and infrastructure will shape the next century.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/rowancheung/recent-activity/all/",
            "date": "2026-06-04",
            "score": "8",
            "reasoning": "AI newsletter recap. Great for understanding global AI trends and summarizing recent news.",
            "comment": "Great recap as always, Rowan. The progress in text-to-video models (Sora, Kling, Luma) is closing the gap for spatial simulators. It will be interesting to see how robotics teams use these video generators for synthetic data and world model pretraining.",
            "likes": "5400",
            "comments": "310",
            "text": "The 5 biggest AI updates of the week: 1. OpenAI launches GPT-4o voice mode globally. 2. Figure AI deploys humanoids to BMW production line. 3. DeepSeek releases Open-Source V3 model. 4. Google updates Gemini 1.5 Pro with 2M context. 5. Luma Dream Machine video generator goes viral.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/alliekmiller/recent-activity/all/",
            "date": "2026-06-03",
            "score": "8",
            "reasoning": "Thought leadership on AI adoption in enterprise, metrics, ROI, and change management. High commentability.",
            "comment": "True enterprise ROI shifts when we move from simple productivity chatbots to autonomous agents integrated into ERP databases. The bottleneck isn't the model API, it's the lack of legacy API wrappers and data governance. Spot-on assessment, Allie.",
            "likes": "4120",
            "comments": "290",
            "text": "Stop asking how many employees are using ChatGPT. Instead, ask: what workflows have we completely automated using AI agents? Enterprise AI adoption is transitioning from productivity gains to autonomous workflows. Measure the outcomes, not the seat licenses.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/clementdelangue/recent-activity/all/",
            "date": "2026-06-02",
            "score": "8",
            "reasoning": "Hugging Face CEO discussing open source AI models and community-driven progress. Excellent thought leadership.",
            "comment": "Open source is indeed driving the developer ecosystem, Clement. The rise of DeepSeek and Llama models proves that closed-source APIs are losing their moat. Hugging Face remains the absolute hub for this collaborative ecosystem.",
            "likes": "6200",
            "comments": "410",
            "text": "Open-source AI models are now matching or outperforming proprietary APIs on core benchmarks. The community-driven approach is more collaborative, secure, and cost-effective. Hugging Face now hosts over 1 million models, and the momentum is unstoppable.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/jeff-dean-5056/recent-activity/all/",
            "date": "2026-05-31",
            "score": "9",
            "reasoning": "Highly technical post by Google Chief Scientist on TPU architectures and model scaling optimization.",
            "comment": "The optimization of TPU v5 clusters for sparse mixture-of-experts (MoE) is a massive engineering feat, Jeff. How are you addressing inter-node communication latency during hot routing phases in model inference at scale?",
            "likes": "8100",
            "comments": "512",
            "text": "Our new TPU v5e and v5p clusters are designed to optimize both training throughput and inference cost. By integrating custom optical circuit switches (OCS) and co-designing hardware with our JAX compiler, we are achieving 2.5x price-performance improvements for sparse Mixture of Experts (MoE) models.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/daniela-rus-637996/recent-activity/all/",
            "date": "2026-05-30",
            "score": "9",
            "reasoning": "MIT CS&AI Lab director sharing research on liquid neural networks for continuous-time robotics control.",
            "comment": "Liquid neural networks are a game-changer for drone control and real-time navigation, Daniela. The ability to adapt to changes in environment variables with small parameter counts is critical for edge deployment. How does the training stability compare to standard RNNs?",
            "likes": "4900",
            "comments": "310",
            "text": "Liquid Neural Networks, inspired by biological brains, are showing incredible promise in robotics. Unlike traditional neural networks that are frozen after training, liquid networks can adapt dynamically to new data streams. Their compact size makes them perfect for edge devices like drones.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/rodney-brooks-11488b3/recent-activity/all/",
            "date": "2026-05-29",
            "score": "8",
            "reasoning": "Robotics pioneer sharing realistic takes on humanoid robots, hardware limitations, and physical constraints.",
            "comment": "Your pragmatism is always refreshing, Rodney. The mechanical reliability (joints, gears, heat dissipation) is indeed a bigger bottleneck than the neural network brains. Humanoids in real warehouses need to hit a 10,000-hour mean time between failures (MTBF) to make economic sense.",
            "likes": "3500",
            "comments": "280",
            "text": "Every tech investor is excited about humanoid robots right now. But hardware is hard. Building a robot that can walk is easy; building one that can run 20 hours a day, 7 days a week, in a dusty warehouse, with a payload, and not break down for years, is a massive mechanical challenge.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/geordierose/recent-activity/all/",
            "date": "2026-05-28",
            "score": "9",
            "reasoning": "CEO of Sanctuary AI sharing video of Phoenix humanoid doing precise manipulation tasks.",
            "comment": "The hand dexterity and force feedback on Phoenix look impressive, Geordie. Teleoperation with haptic suits is a great way to bootstrap the training dataset. Are you using reinforcement learning to generalize the hand movements, or is it mostly imitation learning?",
            "likes": "4210",
            "comments": "295",
            "text": "Our Phoenix humanoid robot is powered by Carbon, our AI control system designed to give robots human-like intelligence. In our latest test, Phoenix is performing precision assembly work. The key is in the hand: 20 degrees of freedom and advanced haptic feedback for delicate manipulation.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/meloneewise/recent-activity/all/",
            "date": "2026-05-27",
            "score": "8",
            "reasoning": "Robotics executive discussing AMR interoperability standards (VDA 5050) and warehouse software automation.",
            "comment": "VDA 5050 is a start, Melonee, but it's too rigid for high-dynamic setups. We need a unified API standard at the orchestration layer that handles active obstacle avoidance and path negotiation dynamically. Glad to see you driving this discourse.",
            "likes": "2900",
            "comments": "180",
            "text": "If we want warehouse automation to scale, we need interoperability. A single warehouse shouldn't require five different proprietary fleet managers for five different types of robots. Open standards like VDA 5050 are critical to allow AMRs from different vendors to work together.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/chris-and-97a61a/recent-activity/all/",
            "date": "2026-05-26",
            "score": "8",
            "reasoning": "Drone pioneer and AI executive discussing drone software, edge computation, and computer vision.",
            "comment": "Edge AI chipsets (like Jetson Orin Nano) are really unlocking real-time SLAM and obstacle avoidance on micro-drones. The next frontier is visual-inertial odometry that runs under 5W. Exciting times, Chris.",
            "likes": "3100",
            "comments": "210",
            "text": "Drones are transitioning from simple remote-controlled cameras to autonomous edge devices. By running computer vision models directly on small companion computers, drones can now map structures and navigate indoor environments without GPS or cloud connection.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/jonathan-hurst-385a49b/recent-activity/all/",
            "date": "2026-05-25",
            "score": "9",
            "reasoning": "Chief Robot Officer of Agility Robotics sharing update on Digit humanoid deployment.",
            "comment": "Digit's backwards-walking legs are a smart design choice for walking on slopes and navigating narrow warehouse aisles, Jonathan. How are you resolving the charging cycle logistics? Can Digit hot-swap battery packs, or does it dock autonomously?",
            "likes": "5120",
            "comments": "340",
            "text": "Digit is now working in Amazon warehouses, moving tote boxes from conveyor belts to shelves. This is a major milestone for the robotics industry. We designed Digit to work in human spaces, alongside humans, to solve labor shortages. This is just the beginning of commercial humanoid deployment.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/elonmusk/recent-activity/all/",
            "date": "2026-05-24",
            "score": "9",
            "reasoning": "Tesla CEO posting about Optimus humanoid robot progress, mass production timeline, and AI chip integration.",
            "comment": "Running the entire FSD network on the robot's onboard Dojo-derived computer is a bold engineering bet. If the actuators can be manufactured at automotive scale and cost, the economic disruption will be massive. When do you expect the first fully autonomous tasks in the Tesla factories?",
            "likes": "28000",
            "comments": "2500",
            "text": "Optimus Gen 2 is walking around the lab and starting to perform simple tasks in our factories. It runs on the same FSD computer and AI network as our cars. We expect to have several thousand Optimus robots working in Tesla factories next year, with mass production for external customers in 2027.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/gdbrockman/recent-activity/all/",
            "date": "2026-05-23",
            "score": "9",
            "reasoning": "OpenAI co-founder sharing insight on training super-large models and cluster hardware scaling challenges.",
            "comment": "Distributed training across multi-node clusters over InfiniBand networks is where the real engineering battle is won, Greg. The hardware failures at this scale are constant. How is OpenAI mitigating training checkpoint serialization overhead?",
            "likes": "7800",
            "comments": "490",
            "text": "Training large-scale AI models is as much a systems engineering problem as it is an AI research problem. Co-orchestrating tens of thousands of GPUs, optimizing network topology, and preventing training runs from crashing due to single-node failures requires incredible systems work.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/mustafasuleyman/recent-activity/all/",
            "date": "2026-05-22",
            "score": "8",
            "reasoning": "CEO of Microsoft AI discussing user interaction models, voice agents, and the future of consumer AI.",
            "comment": "Voice interaction with latency below 300ms is the tipping point where AI feels like a natural conversation partner. The challenge is handling speech interruptions and context tracking during long dialogs. Exciting updates, Mustafa.",
            "likes": "6300",
            "comments": "510",
            "text": "We are designing Copilot to be an emotional and intellectual assistant that supports you throughout the day. With natural voice interfaces and real-time vision capabilities, your AI companion will be able to see what you see, listen to you, and help you interact with the digital world.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/thomasdohmke/recent-activity/all/",
            "date": "2026-05-21",
            "score": "8",
            "reasoning": "GitHub CEO sharing progress on Copilot Workspace and the future of developer workflows.",
            "comment": "Moving from inline code completion to repository-level workspace agents is the right direction, Thomas. The developer shifts from a writer of code to a reviewer and system architect. How do you plan to handle complex multi-file debugging loops in legacy codebases?",
            "likes": "5200",
            "comments": "310",
            "text": "GitHub Copilot Workspace is our vision for natural language coding. Developers can now express their ideas in plain English, and the workspace agent will plan the edits, modify files, run tests, and open a Pull Request. Coding is becoming accessible to everyone.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/aravindsrinivas/recent-activity/all/",
            "date": "2026-05-20",
            "score": "8",
            "reasoning": "Perplexity CEO sharing thoughts on conversational search, citation accuracy, and search user experience.",
            "comment": "The core value of Perplexity is citation verification. By grounding LLM reasoning in index search results, you minimize hallucinations. How do you plan to scale the indexing infrastructure to handle real-time social media search?",
            "likes": "4800",
            "comments": "395",
            "text": "Traditional search is dead. People don't want a list of 10 links; they want direct, verified answers with citations. Conversational search is about combining large language models with real-time web indexes to give users the ground truth instantly.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/vinodkhosla/recent-activity/all/",
            "date": "2026-05-19",
            "score": "8",
            "reasoning": "Veteran venture capitalist sharing predictions on AI, economic impact, and future labor markets.",
            "comment": "Free cognitive labor will indeed restructure the services sector, Vinod. The key is how quickly we can scale physical robotics hardware to automate manual labor. The bottleneck is the high cost of mechanical actuators.",
            "likes": "6800",
            "comments": "690",
            "text": "In 10 years, AI will be able to perform almost all cognitive labor. Medical diagnostics, legal contracts, coding, and teaching will be near-free. This will lead to unprecedented abundance, but we must prepare for the massive shift in labor markets and tax systems.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/aidangomez/recent-activity/all/",
            "date": "2026-05-18",
            "score": "8",
            "reasoning": "Cohere CEO sharing insights on fine-tuning LLMs for specific enterprise domains.",
            "comment": "Fine-tuning models on proprietary enterprise data with parameter-efficient techniques (like LoRA) is far more secure and accurate for corporate compliance than general APIs. Appreciate Cohere's enterprise-first focus, Aidan.",
            "likes": "3500",
            "comments": "210",
            "text": "Enterprises don't need general chatbot models; they need models that speak their corporate language, understand their databases, and respect data privacy constraints. Fine-tuning models on proprietary data is the only way to build secure, domain-specific AI.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/noamshazeer/recent-activity/all/",
            "date": "2026-05-17",
            "score": "8",
            "reasoning": "AI pioneer discussing reasoning architectures and user engagement patterns in dialog agents.",
            "comment": "The latency budget for chat agents dictates the complexity of the reasoning path. Dynamic routing (using quick models for chit-chat and heavy reasoning models for multi-step prompts) is essential. Great insights, Noam.",
            "likes": "4900",
            "comments": "320",
            "text": "The next major breakthrough is not just predicting the next word, but incorporating reasoning steps into the inference cycle. By allocating computation time dynamically based on prompt complexity, models will behave more like human thinkers who pause to reflect before answering.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/socher/recent-activity/all/",
            "date": "2026-05-16",
            "score": "8",
            "reasoning": "AI researcher and founder sharing updates on multi-agent search systems and reasoning.",
            "comment": "Orchestrating multiple specialized agents (e.g. Writer agent, Search agent, Code runner agent) yields far better structured research reports than a single prompt. Spot-on architecture demonstration, Richard.",
            "likes": "2900",
            "comments": "195",
            "text": "Our new multi-agent search engine doesn't just fetch answers. It spawns a researcher agent, a writer agent, and a fact-checker agent that work in parallel to compile a comprehensive, cited report on any topic. This is the future of digital knowledge workers.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/daphne-koller-17215/recent-activity/all/",
            "date": "2026-05-15",
            "score": "9",
            "reasoning": "AI pioneer sharing research on scaling machine learning models for drug discovery and genetics.",
            "comment": "The combination of high-throughput automated biology labs and machine learning represents a paradigm shift for clinical trials, Daphne. Moving from heuristic molecular design to generative drug target synthesis will save millions of lives.",
            "likes": "4500",
            "comments": "290",
            "text": "Machine learning is completely transforming biology. At Insitro, we are combining robotic automation in wet labs with deep learning models to predict how candidate compounds interact with human cells. This allows us to find disease-fighting molecules at a fraction of the cost of traditional pharma.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/percy-liang-22a846b/recent-activity/all/",
            "date": "2026-05-14",
            "score": "8",
            "reasoning": "Stanford professor discussing model evaluation benchmarks and safety alignment tracking.",
            "comment": "Standard static benchmarks (like MMLU) are saturated and subject to data contamination. We need dynamic evaluation benchmarks like HELM that continuously test models with out-of-distribution reasoning prompts. Excellent work, Percy.",
            "likes": "3100",
            "comments": "210",
            "text": "Model evaluation is broken. Standard benchmarks are increasingly leaked into the training datasets. Our latest Holistic Evaluation of Language Models (HELM) introduces dynamic evaluations to measure safety, bias, reasoning accuracy, and code execution across 50+ open and closed models.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/joelle-pineau-1b07297/recent-activity/all/",
            "date": "2026-05-13",
            "score": "8",
            "reasoning": "AI researcher discussing reproducibility, open science, and peer review in machine learning.",
            "comment": "Reproducibility is the bedrock of scientific progress, Joelle. Requiring code, environment configs, and training logs alongside papers is crucial to filter out cherry-picked baseline results. Thank you for advocating for this.",
            "likes": "2800",
            "comments": "190",
            "text": "As AI research accelerates, the reproducibility crisis in machine learning is worsening. We must make it standard practice to publish code, hyperparameter settings, and data split files alongside our papers. Open science is only open if it is reproducible.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/raquel-urtasun-995775b/recent-activity/all/",
            "date": "2026-05-12",
            "score": "9",
            "reasoning": "Founder of Waabi presenting generative simulator for training autonomous trucks.",
            "comment": "Using closed-loop generative simulation to train autonomous driving policies is the only way to expose models to edge-case accidents safely, Raquel. The fidelity of Waabi World's sensor reconstruction looks incredibly realistic.",
            "likes": "4900",
            "comments": "312",
            "text": "I am excited to share Waabi World, our closed-loop simulator that uses generative AI to build realistic virtual test environments. We can simulate millions of driving scenarios, including rare edge-case accidents, to train our autonomous truck brain. This accelerates deployment without needing million-mile public road tests.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/david-silver-8bb84b/recent-activity/all/",
            "date": "2026-05-11",
            "score": "9",
            "reasoning": "DeepMind researcher sharing insights on RL scaling laws and model-free planning.",
            "comment": "Model-free reinforcement learning coupled with search (like AlphaGo/MuZero) remains the most elegant path to superhuman performance. How do you view applying these methods to unstructured physical tasks like robotic kitchen cleaning?",
            "likes": "5600",
            "comments": "380",
            "text": "Reinforcement learning (RL) combined with search is the fundamental architecture of intelligent decision making. While LLMs are great at text representation, RL allows agents to discover novel solutions that humans have never written down. Scalable RL is the key to solving general robotics control.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/oriolvinyals/recent-activity/all/",
            "date": "2026-05-10",
            "score": "9",
            "reasoning": "Google DeepMind VP sharing updates on Gemini's multimodal token design.",
            "comment": "Native multimodality (treating pixels, audio, and text in a single shared transformer block) is far superior to late-fusion architectures. It preserves spatial and temporal correlations. Fantastic engineering work, Oriol.",
            "likes": "6100",
            "comments": "410",
            "text": "Gemini was designed from day one to be native multimodal. We don't train separate encoders and stitch them together; we train a single transformer across text, code, audio, image, and video tokens. This allows the model to reason across modalities seamlessly.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/dario-amodei-3a216a4/recent-activity/all/",
            "date": "2026-05-09",
            "score": "9",
            "reasoning": "Anthropic CEO sharing insights on Claude 3.5 Sonnet launch, coding capabilities, and safety evaluations.",
            "comment": "Claude 3.5 Sonnet's agentic coding capability (working on actual repos via tools) represents a massive step. The key is the high accuracy in long-context system prompts. How are you evaluating agent escape risks during sandbox execution?",
            "likes": "7200",
            "comments": "512",
            "text": "We are releasing Claude 3.5 Sonnet. It sets a new industry standard for graduate-level reasoning, undergraduate-level knowledge, and coding proficiency. Along with these capabilities, we have conducted rigorous safety and alignment tests, working with third-party evaluation institutes.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/stevenouri/recent-activity/all/",
            "date": "2026-05-08",
            "score": "8",
            "reasoning": "Popular AI influencer sharing curated technical cheat sheets. High reach and engagement.",
            "comment": "Excellent compilation, Steven. Visual cheat sheets are highly effective for onboarding junior developers to complex ML concepts like attention mechanisms and vector search index layouts. Thanks for sharing.",
            "likes": "15000",
            "comments": "680",
            "text": "Here are the top 10 AI cheat sheets every developer needs in 2026, covering LLM fine-tuning, retrieval-augmented generation (RAG), vector database comparison, and agentic workflows. Download the high-res PDF versions in the comments.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/emollick/recent-activity/all/",
            "date": "2026-05-07",
            "score": "8",
            "reasoning": "Wharton professor writing about using AI in classrooms and co-intelligence frameworks.",
            "comment": "AI as an active co-intelligence tutor that queries the student and provides hints is far more educational than a simple answer-generation box. Spot-on pedagogy, Ethan.",
            "likes": "4500",
            "comments": "310",
            "text": "Instead of banning AI in schools, we must teach students how to work alongside AI as a co-intelligence partner. Those who learn to orchestrate AI models, check their output, and leverage them for brainstorming will be 10x more productive in the future workforce.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/pascalbornet/recent-activity/all/",
            "date": "2026-05-06",
            "score": "8",
            "reasoning": "Thought leader discussing intelligent automation and AI agent deployment frameworks.",
            "comment": "Intelligent automation requires transitioning from rigid robotic process automation (RPA) workflows to goal-driven LLM planner agents. RPA breaks when the web UI changes; LLM agents adapt dynamically. Great point, Pascal.",
            "likes": "3900",
            "comments": "210",
            "text": "Intelligent Automation is moving from simple RPA rules to autonomous cognitive agents. RPA could copy and paste data between screens; cognitive agents can make decisions, resolve invoice discrepancies, and coordinate across systems to complete business goals.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/bernardmarr/recent-activity/all/",
            "date": "2026-05-05",
            "score": "8",
            "reasoning": "Futurist outlining AI and robotics trends for the upcoming years. Good broad engagement.",
            "comment": "The convergence of LLM-based reasoning and humanoid mechanical platforms is the defining tech trend of this decade. It unlocks automation for non-structured physical work. Thanks for the summary, Bernard.",
            "likes": "5400",
            "comments": "340",
            "text": "What is the future of AI and robotics? Here are the top 5 trends: 1. Embodied AI and commercial humanoids. 2. Native multimodal large models. 3. Autonomous agent coordination networks. 4. AI-accelerated scientific research. 5. Edge computing and micro-model deployments.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/ronald-van-loon-597b38/recent-activity/all/",
            "date": "2026-05-04",
            "score": "8",
            "reasoning": "Data influencer sharing video of automated factory floor and discussing IIoT.",
            "comment": "Integrating factory telemetry (Industrial IoT) with large language model interfaces allows operators to query factory line status in natural language. This is a massive win for manufacturing uptime, Ronald.",
            "likes": "8900",
            "comments": "580",
            "text": "Industrial IoT and Big Data are the foundations of the smart factory. By combining real-time sensor streams from robotic lines with predictive maintenance models, manufacturers can predict machine failures days before they occur, saving millions in downtime.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/nathanbenaich/recent-activity/all/",
            "date": "2026-05-03",
            "score": "9",
            "reasoning": "Venture capitalist sharing findings from the annual State of AI Report. High value.",
            "comment": "The consolidation of LLM compute capabilities has made inference costs drop by 99%, Nathan. This is what makes complex agentic loops economically viable. The report's analysis of hardware clusters and geopolitical chip battles is superb.",
            "likes": "4500",
            "comments": "290",
            "text": "The State of AI Report is live. Key takeaways: 1. Inference compute costs have dropped by 100x, enabling deep agent loops. 2. AI hardware clustering is clustering around nuclear and clean energy nodes. 3. Humanoid robots are transitioning from pilot programs to production assembly lines.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/matt-wolfe-ai/recent-activity/all/",
            "date": "2026-05-02",
            "score": "8",
            "reasoning": "AI content creator discussing generative video tools and spatial consistency.",
            "comment": "Spatial consistency in video generators is critical because it means the AI model is learning a physics simulator implicitly. This will feed back into synthetic training data pipelines for humanoid robotics. Great comparison, Matt.",
            "likes": "3800",
            "comments": "250",
            "text": "Generative video tools (Sora, Runaway Gen-3, Luma Dream Machine) are achieving incredible spatial consistency. You can now generate a scene from multiple camera angles and have the objects retain their structure. This is a massive step for digital cinematography.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/linusekenstam/recent-activity/all/",
            "date": "2026-05-01",
            "score": "8",
            "reasoning": "Designer discussing AI product UI/UX and text-based vs canvas interfaces.",
            "comment": "The chatbot interface is just a temporary stepping stone, Linus. The true UX for AI is proactive: background agents performing tasks and presenting results in dynamic canvas interfaces. Thanks for driving this conversation.",
            "likes": "4900",
            "comments": "310",
            "text": "AI product design is moving away from the simple chat box. The chat interface requires too much cognitive load from the user. We are transitioning to canvas-based layouts, generative interfaces, and background agents that present completed drafts for approval.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/bentossell/recent-activity/all/",
            "date": "2026-04-30",
            "score": "8",
            "reasoning": "AI tools directory editor sharing workflow optimization list. Broad appeal.",
            "comment": "Orchestrating tools with simple system integrations (like Make/Zapier or MCP) is where most companies find immediate ROI. Great checklist of tools, Ben.",
            "likes": "4100",
            "comments": "210",
            "text": "Here are 5 AI tools that will save you 10 hours of work this week: 1. Perplexity for research. 2. Cursor for coding. 3. Claude for writing. 4. Granola for meeting notes. 5. Gamma for presentation designs. Stop working hard, start working smart.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/mattschlicht/recent-activity/all/",
            "date": "2026-04-29",
            "score": "8",
            "reasoning": "AI newsletter editor discussing background agent infrastructure and API tools.",
            "comment": "The rise of Model Context Protocol (MCP) by Anthropic is unifying how agents connect to local tools and databases, Matt. It solves the fragmentation problem of custom API connectors. Great analysis.",
            "likes": "3500",
            "comments": "190",
            "text": "The infrastructure layer for AI agents is consolidating. With standards like the Model Context Protocol (MCP), developers can now build a single tool wrapper that can be utilized by Claude, OpenAI, and local LLMs without rewriting code. This accelerates agent interoperability.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/miteshk/recent-activity/all/",
            "date": "2026-04-28",
            "score": "8",
            "reasoning": "Professor sharing updates on academic AI research and publishing trends globally.",
            "comment": "Fostering academic-industry partnerships is vital to commercialize deep tech research. The work you are doing in training the next generation of deep learning researchers is highly commendable, Mitesh.",
            "likes": "2400",
            "comments": "120",
            "text": "Academic AI research must shift from simple benchmarking to solving real-world domain problems. We are building deep partnerships between universities and robotics firms to commercialize research in computer vision, edge SLAM, and physical control algorithms.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/rama-akkiraju-308119/recent-activity/all/",
            "date": "2026-04-27",
            "score": "8",
            "reasoning": "AI executive discussing data governance, copyright issues, and ethical compliance.",
            "comment": "Watermarking training datasets and tracking model provenance is critical for enterprise legal compliance. A robust compliance dashboard is as important as the model evaluation stack itself. Appreciate your focus on this, Rama.",
            "likes": "3100",
            "comments": "195",
            "text": "AI governance is no longer just a policy conversation; it's a technical requirement. Enterprises need tools to track data lineage, verify training rights, detect bias in model outputs, and enforce compliance guidelines in real-time agent deployments.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/linxi-fan-7a242a37/recent-activity/all/",
            "date": "2026-04-26",
            "score": "9",
            "reasoning": "Nvidia AI researcher sharing breakthrough on embodied AI agents in virtual environments.",
            "comment": "Voyager's code-as-action space is a highly scalable framework, Linxi. By saving successful code snippets to a skill library, the agent learns incrementally without retraining neural weights. How are you mapping this to continuous physical robot controllers?",
            "likes": "6500",
            "comments": "410",
            "text": "Our Voyager agent in Minecraft is the first LLM-powered embodied agent that plays the game continuously. Voyager uses an active learning loop: it writes code to execute actions, receives feedback from the simulator, refines the code, and saves successful skills to its memory. This is lifelong learning in action.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/linxi-fan-7a242a37/recent-activity/all/",
            "date": "2026-04-25",
            "score": "10",
            "reasoning": "Nvidia research lead sharing progress on Project GR00T foundation model for humanoid robots.",
            "comment": "Project GR00T is a landmark initiative, Jim. Having a unified foundation model that takes multimodal inputs (vision, language, forces) and outputs motor controls will accelerate humanoid versatility. How are you addressing the sim-to-real gap for fine motor skills?",
            "likes": "9800",
            "comments": "690",
            "text": "Nvidia is launching Project GR00T, a general-purpose foundation model for humanoid robots. GR00T enables robots to understand natural language, mimic human movements by observing video, and navigate the physical world. We are partnering with Agility, Unitree, Figure, and UBTECH to deploy it.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/alliekmiller/recent-activity/all/",
            "date": "2026-04-24",
            "score": "8",
            "reasoning": "AI leader reviewing agent orchestration libraries like LangGraph and CrewAI.",
            "comment": "The challenge with graph-based agent libraries is debugging state transitions when the loop gets stuck. Simple, explicit state machines are often more reliable in production. Great review of the ecosystem, Allie.",
            "likes": "3500",
            "comments": "230",
            "text": "Which agent orchestration library should you choose? LangGraph is great for cyclic, graph-based agents; CrewAI is perfect for role-playing, multi-agent setups; and Semantic Kernel is ideal for enterprise C# integration. Choose the library that matches your backend architecture.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/clementdelangue/recent-activity/all/",
            "date": "2026-04-23",
            "score": "9",
            "reasoning": "Hugging Face CEO announcing open-source robotics initiative LeRobot.",
            "comment": "LeRobot is an excellent initiative, Clement. Democratizing robotics data and control loops via open source is the only way to accelerate physical AI. Having cheap hardware designs (like SO-ARM) that run on open models is exactly what the developer community needs.",
            "likes": "5400",
            "comments": "310",
            "text": "We are launching LeRobot, an open-source robotics library designed to make AI for robotics accessible to everyone. We are providing open-source models, training datasets, and hardware designs for low-cost robotic arms. The future of robotics is open.",
            "category": "global"
        },
        {
            "url": "https://www.linkedin.com/in/brettadcock/recent-activity/all/",
            "date": "2026-04-22",
            "score": "9",
            "reasoning": "CEO of Figure sharing video of Figure 01 robot operating a coffee machine by observing humans.",
            "comment": "The end-to-end neural network learning of physical interactions (inserting pod, pressing button, reacting to placement) is a huge step forward, Brett. It proves that we don't need hand-coded heuristics for every object interaction. How long was the training cycle?",
            "likes": "8900",
            "comments": "540",
            "text": "Here is Figure 01 making coffee. It observed a human make coffee for 10 hours, and it learned how to do it end-to-end. There are no programmed routines; it is mapping vision tokens directly to joint control outputs in real time. This is the power of neural network control.",
            "category": "global"
        }
    ]
    
    # 20 Chinese Influencer Posts
    chinese_posts = [
        {
            "url": "https://cn.linkedin.com/in/kaifulee/recent-activity/all/",
            "date": "2026-06-13",
            "score": "9",
            "reasoning": "Major model launch by 01.AI CEO. Highlights competitive performance of Chinese LLMs on global leaderboards.",
            "comment": "Congratulations on the launch of Yi-Lightning, Dr. Lee. Achieving top rankings on LMSYS Chatbot Arena at a fraction of the cost per million tokens is a massive win for open-weight models. How do you plan to leverage Yi-Lightning for embodied AI applications in Sinovation's robotics portfolio?",
            "likes": "3520",
            "comments": "212",
            "text": "01.AI's new model Yi-Lightning is now ranked #1 among Chinese models and top-tier globally on the LMSYS leaderboard, matching GPT-4o. We are proving that Chinese AI startups can deliver world-class reasoning models with superior cost-efficiency. Our focus is on bringing cost-effective, high-reasoning capabilities to global enterprise markets.",
            "category": "chinese"
        },
        {
            "url": "https://www.linkedin.com/company/baidu/recent-activity/all/",
            "date": "2026-06-12",
            "score": "9",
            "reasoning": "CEO of Baidu sharing performance metrics and API call counts for ERNIE model ecosystem.",
            "comment": "ERNIE's API query volume (exceeding 600 million daily calls) is an impressive scaling achievement, Robin. How are you optimizing GPU memory caching to handle concurrent multi-modal agent workflows on Baidu Cloud's Ascend clusters?",
            "likes": "4210",
            "comments": "310",
            "text": "Baidu's ERNIE Bot model family is now processing over 600 million API requests daily. We are building a robust AI application ecosystem in China. The real value of AI is not in training the biggest model, but in building the most useful applications that solve industrial, enterprise, and logistics problems.",
            "category": "chinese"
        },
        {
            "url": "https://www.linkedin.com/company/unitree/recent-activity/all/",
            "date": "2026-06-11",
            "score": "10",
            "reasoning": "Major announcement of low-cost humanoid robot (Unitree G1 at $16k) and mass production readiness by Unitree founder.",
            "comment": "At $16,000, the Unitree G1 completely resets the economics of humanoid robotics, Wang. Mass manufacturing these with integrated 3D LiDAR and force-controlled hands will accelerate research labs worldwide. When do you expect the first batch of customer deliveries?",
            "likes": "8900",
            "comments": "720",
            "text": "We are starting mass production of the Unitree G1 humanoid robot. Priced at $16,000, it is designed to be affordable and robust. G1 is equipped with 3D LiDAR, depth cameras, and custom joint actuators that allow it to perform running, high-jumps, and delicate object manipulation. Robotics is transitioning from research to consumer product.",
            "category": "chinese"
        },
        {
            "url": "https://www.linkedin.com/company/xpeng-motors/recent-activity/all/",
            "date": "2026-06-10",
            "score": "9",
            "reasoning": "XPENG CEO sharing video of humanoid robot working in automotive factory. High relevance to Physical AI.",
            "comment": "Nesting humanoid robots directly into the smart manufacturing loop is a logical evolution, He. The hand-arm coordination on the PX5 looks highly precise. Are you training the manipulation tasks using reinforcement learning in simulation, or direct teleoperation cloning?",
            "likes": "5120",
            "comments": "295",
            "text": "XPENG's humanoid robot PX5 is now running test operations in our smart EV manufacturing facilities in Zhaoqing. The robot is training on assembly line tasks: picking components, placing wiring harnesses, and performing quality checks. By integrating humanoid robots with automotive manufacturing, we are optimizing automation.",
            "category": "chinese"
        },
        {
            "url": "https://www.linkedin.com/company/ubtech-robotics/recent-activity/all/",
            "date": "2026-06-09",
            "score": "9",
            "reasoning": "UBTECH CEO announcing pilot program of Walker S humanoid robot in NIO EV factory. High-value industry announcement.",
            "comment": "The pilot with NIO is a massive step for industrial humanoid validation, Zhou. The force-controlled assembly of vehicle doors is a high-accuracy task. How is the Walker S handling safety protocols when working alongside human operators in the assembly cell?",
            "likes": "4300",
            "comments": "210",
            "text": "UBTECH's industrial humanoid robot Walker S has successfully completed its pilot deployment in NIO's advanced EV factory. Walker S performed tasks such as vehicle quality inspections, seat belt installations, and component picking. Humanoid robots are ready to enter heavy industrial assembly lines.",
            "category": "chinese"
        },
        {
            "url": "https://www.linkedin.com/company/sensetime/recent-activity/all/",
            "date": "2026-06-08",
            "score": "8",
            "reasoning": "SenseTime CEO sharing updates on SenseNova 5.5 model launch and edge-side deployment.",
            "comment": "SenseNova 5.5's edge-side execution capabilities open up great possibilities for local robotic control loops, Xu. Running a high-performance vision-language-action (VLA) model locally under low latency is crucial. How many parameters are dedicated to the visual encoder?",
            "likes": "3100",
            "comments": "180",
            "text": "We are releasing SenseNova 5.5, which features advanced real-time multimodal reasoning. Our model optimizes edge-side deployment, allowing smart devices and collaborative robots to process visual and audio streams locally with sub-100ms latency. We are empowering edge intelligence.",
            "category": "chinese"
        },
        {
            "url": "https://www.linkedin.com/company/megvii-technology/recent-activity/all/",
            "date": "2026-06-07",
            "score": "8",
            "reasoning": "Megvii CEO sharing updates on automated warehouse management systems using physical AI models.",
            "comment": "Integrating deep-learning-based 3D bin packing with multi-agent AMR routing is where true efficiency lies, Yin. Standard heuristic systems fail when item geometry is highly variable. Your physical AI approach is showing the way.",
            "likes": "2800",
            "comments": "150",
            "text": "Megvii is applying Physical AI models to warehouse logistics. Our smart AMRs and robotic arms are now using a shared coordinate system and visual world models to optimize automated picking, sorting, and high-density storage. The software is learning to understand physical space.",
            "category": "chinese"
        },
        {
            "url": "https://www.linkedin.com/company/horizon-robotics/recent-activity/all/",
            "date": "2026-06-06",
            "score": "8",
            "reasoning": "Horizon Robotics CEO sharing details on new auto chip launch and autonomous driving partnerships.",
            "comment": "The Journey 6 chip's design (specifically the hardware acceleration for transformer blocks) is crucial for end-to-end autonomous driving networks, Yu. Are you seeing Chinese OEMs move completely to end-to-end models (like UniAD) on this silicon?",
            "likes": "3900",
            "comments": "210",
            "text": "We are launching the Horizon Journey 6 chip series, designed specifically for intelligent driving systems. With custom hardware engines that optimize neural networks (especially vision transformers), Journey 6 enables low-power, high-compute autonomous driving. We are proud to partner with leading automakers.",
            "category": "chinese"
        },
        {
            "url": "https://www.linkedin.com/company/agibot/recent-activity/all/",
            "date": "2026-06-05",
            "score": "10",
            "reasoning": "Major post by AGIBOT founder (famous creator Peng Zhihui/Wilder) announcing Raise A1 humanoid and open source framework. Highly popular.",
            "comment": "The Raise A1 showcases incredible speed in development, Zhihui. The open-source SDK and modular joint design will foster a strong community of developers. Are you focusing on standard ROS 2 node wrappers or did you implement a custom lightweight middleware for low-latency joint control?",
            "likes": "12000",
            "comments": "950",
            "text": "AGIBOT is introducing the Raise A1 humanoid robot. We are committed to an open-source robotics ecosystem. We are open-sourcing our joint actuator schematics, motion control algorithms, and our robot SDK. By lowering the barrier for developers, we hope to accelerate the arrival of embodied AI in homes and factories.",
            "category": "chinese"
        },
        {
            "url": "https://www.linkedin.com/company/zhipu-ai/recent-activity/all/",
            "date": "2026-06-04",
            "score": "9",
            "reasoning": "CEO of Zhipu AI announcing open weights for GLM-4-9B, featuring long context and advanced reasoning.",
            "comment": "GLM-4-9B's performance on long context benchmarks (128K context window with near-perfect retrieval) is outstanding, Zhang. Providing this model open-weight enables developers to deploy high-quality local RAG applications easily. Thanks for supporting the open community.",
            "likes": "4500",
            "comments": "310",
            "text": "We are proud to release the open-weights for GLM-4-9B, our latest large language model. GLM-4-9B supports a 128K context window, multi-language tasks, and advanced function calling. We believe that open weights are essential to foster global AI innovation and research.",
            "category": "chinese"
        },
        {
            "url": "https://www.linkedin.com/company/baidu/recent-activity/all/",
            "date": "2026-06-03",
            "score": "8",
            "reasoning": "Baidu CTO sharing updates on industrial AI applications, agent templates, and cloud scalability.",
            "comment": "Deploying ERNIE-powered agents directly into manufacturing telemetry pipelines is a great use-case, Haifeng. Natural language diagnostics for machine operators drastically reduces repair search time. Appreciate you sharing the metrics.",
            "likes": "2400",
            "comments": "140",
            "text": "We are expanding the industrial application templates for the ERNIE platform. By providing pre-built agent architectures for quality inspection, machine diagnostics, and supply chain routing, we are making it easy for energy and manufacturing sectors to deploy AI.",
            "category": "chinese"
        },
        {
            "url": "https://www.linkedin.com/company/tsinghua-university/recent-activity/all/",
            "date": "2026-06-02",
            "score": "9",
            "reasoning": "Tsinghua Dean sharing academic research on embodied intelligence, sim-to-real translation, and robot control.",
            "comment": "Your research on using generative video models as world simulators for sim-to-real transfer is highly innovative, Dr. Zhang. It addresses the main bottleneck of physical data collection. Tsinghua's AIR lab continues to produce world-class work.",
            "likes": "3200",
            "comments": "210",
            "text": "At Tsinghua's Institute for AI Industry Research (AIR), we are focusing on embodied intelligence. Our latest work introduces a generative simulator that translates synthetic simulation controls directly to real physical hardware, bypassing typical sim-to-real errors. Fostering industry-academia collaboration is our key mission.",
            "category": "chinese"
        },
        {
            "url": "https://www.linkedin.com/company/360-security-group/recent-activity/all/",
            "date": "2026-06-01",
            "score": "8",
            "reasoning": "CEO of 360 Group discussing AI safety, LLM security, and cybersecurity agents.",
            "comment": "Secure-by-design AI agents are critical, Hongyi. An LLM agent with direct database write access must be surrounded by robust input-validation wrappers and sandbox controls. Appreciate your focus on security.",
            "likes": "4100",
            "comments": "310",
            "text": "As AI models get more autonomous, LLM security is becoming the new cybersecurity frontier. At 360 Group, we are building specialized security agents that monitor LLM inputs and outputs to prevent prompt injection, data leakage, and unauthorized tool calls in enterprise networks.",
            "category": "chinese"
        },
        {
            "url": "https://www.linkedin.com/company/jd.com/recent-activity/all/",
            "date": "2026-05-30",
            "score": "8",
            "reasoning": "JD.com founder sharing video of fully automated sorting center and driverless delivery vans.",
            "comment": "The density of AMRs in JD's smart fulfillment centers is remarkable, Richard. Coordinating hundreds of robots in a dynamic layout without collisions requires excellent central task orchestration. Thanks for sharing the video.",
            "likes": "4900",
            "comments": "280",
            "text": "JD Logistics is expanding its driverless delivery network. Our automated fulfillment centers now handle over 90% of sorting tasks using smart robotic AMRs. We are deploying autonomous delivery vans in municipal zones to bridge the last-mile logistics gap efficiently.",
            "category": "chinese"
        },
        {
            "url": "https://www.linkedin.com/company/huawei/recent-activity/all/",
            "date": "2026-05-29",
            "score": "9",
            "reasoning": "Huawei Chairman sharing details on Ascend chip scaling, compiler optimizations, and cluster benchmarks.",
            "comment": "The CANN software architecture improvements are crucial for Ascend's developer ecosystem, Zhijun. Optimizing model-parallel communications over custom networking adapters is what unlocks training scaling. Great engineering progress.",
            "likes": "6200",
            "comments": "450",
            "text": "Huawei continues to scale its Ascend AI hardware ecosystem. With our MindSpore framework and CANN software architecture, we are optimizing training cluster efficiency, allowing enterprises to train massive LLMs on Ascend clusters with near-linear scaling performance.",
            "category": "chinese"
        },
        {
            "url": "https://www.linkedin.com/company/li-auto/recent-activity/all/",
            "date": "2026-05-28",
            "score": "8",
            "reasoning": "CEO of Li Auto sharing video of end-to-end autonomous driving model in heavy traffic.",
            "comment": "End-to-end neural networks (mapping camera streams directly to steering/braking controls) handle dense traffic much more naturally than rule-based planners. The vehicle's lane merge in the video was incredibly smooth, Xiang.",
            "likes": "4500",
            "comments": "290",
            "text": "Li Auto's new end-to-end (E2E) autonomous driving model is now rolling out to our L-series customers. The E2E network processes camera frames and outputs steering angle and speed directly, resulting in smoother human-like driving, especially in chaotic urban traffic environments.",
            "category": "chinese"
        },
        {
            "url": "https://www.linkedin.com/company/nio/recent-activity/all/",
            "date": "2026-05-27",
            "score": "8",
            "reasoning": "NIO CEO sharing video of automated battery swapping station operated by robotic arms.",
            "comment": "Replacing a battery pack in under 3 minutes using robotic automation is a major convenience moat, William. The alignment precision of the torque-controlled bolts on the robotic gantry is impressive.",
            "likes": "5100",
            "comments": "320",
            "text": "NIO has completed over 40 million battery swaps globally. Our Gen 4 swapping stations are fully automated: the car parks itself, and a robotic gantry swaps the battery pack in 2 minutes and 40 seconds. We are combining smart EV technology with industrial robotics.",
            "category": "chinese"
        },
        {
            "url": "https://www.linkedin.com/company/werideai/recent-activity/all/",
            "date": "2026-05-26",
            "score": "8",
            "reasoning": "WeRide CEO sharing commercial robotaxi deployment updates in Guangzhou and global markets.",
            "comment": "Scaling driverless commercial robotaxis requires robust remote assistance nodes and low-latency safety streaming. Having deployments in multiple cities worldwide shows WeRide's regulatory and technical maturity, Tony.",
            "likes": "3800",
            "comments": "190",
            "text": "WeRide is expanding its driverless robotaxi operations. We have received approval to operate commercial driverless passenger services in Guangzhou, and are scaling our fleets in Abu Dhabi and Singapore. Autonomous mobility is no longer a pilot; it's a public utility.",
            "category": "chinese"
        },
        {
            "url": "https://www.linkedin.com/company/moonshot-ai/recent-activity/all/",
            "date": "2026-05-25",
            "score": "9",
            "reasoning": "CEO of Moonshot AI discussing long-context windows (Kimi) and its application to long-horizon agents.",
            "comment": "A 2-million token context window allows an agent to read entire codebases or research histories directly in memory, Zhilin. It eliminates RAG indexing errors for complex queries. How are you maintaining retrieval needle-in-a-haystack accuracy at this scale?",
            "likes": "6800",
            "comments": "512",
            "text": "Our chatbot Kimi now supports 2 million characters of context. Long context is key to true intelligence. It allows the model to have deep memory: you can upload a whole textbook, a complete codebase, or financial histories, and Kimi can reason and write code across the entire dataset.",
            "category": "chinese"
        },
        {
            "url": "https://www.linkedin.com/company/deepseek/recent-activity/all/",
            "date": "2026-05-24",
            "score": "10",
            "reasoning": "DeepSeek founder sharing architectural details on DeepSeek-V3 and its extreme training cost-efficiency. Highly impactful globally.",
            "comment": "DeepSeek-V3's training cost (under $6M for 671B parameters) is a monumental engineering accomplishment, Liang. Multi-head latent attention (MLA) and auxiliary-loss-free load balancing are brilliant innovations. It completely disrupts the traditional compute-heavy scaling assumptions.",
            "likes": "14000",
            "comments": "1200",
            "text": "We are releasing DeepSeek-V3, a 671B parameter Mixture-of-Experts model. We trained it on 14.8 trillion tokens for only $5.5 million in compute costs. By introducing Multi-head Latent Attention (MLA) and DualPipe overlapping communications, we achieved state-of-the-art performance with 10x training efficiency.",
            "category": "chinese"
        }
    ]
    
    # Write to CSV
    keys = ['url', 'date', 'score', 'reasoning', 'comment', 'likes', 'comments', 'text', 'category']
    
    # Sort merged list by score descending
    all_seeded_posts = global_posts + chinese_posts
    all_seeded_posts.sort(key=lambda x: int(x['score']), reverse=True)
    
    print(f"[*] Seeding {len(all_seeded_posts)} posts (50 global + 20 Chinese) to {csv_file}...")
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for post in all_seeded_posts:
            writer.writerow(post)
            
    # Seed into SQLite
    from src.database import init_db, get_db_connection
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("[*] Seeding posts into SQLite database...")
    for post in all_seeded_posts:
        # Check if profile_id can be matched
        profile_id = None
        cursor.execute("SELECT id FROM profiles WHERE url = ?", (post['url'],))
        p_row = cursor.fetchone()
        if p_row:
            profile_id = p_row['id']
            
        cursor.execute("""
        INSERT INTO posts (url, profile_id, post_text, likes, comments, published_date, category, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'scored')
        ON CONFLICT(url) DO UPDATE SET
            post_text = excluded.post_text,
            likes = excluded.likes,
            comments = excluded.comments,
            published_date = excluded.published_date,
            status = 'scored'
        """, (
            post['url'], profile_id, post['text'], 
            int(post['likes']), int(post['comments']), 
            post['date'], post['category']
        ))
        
        # Get post_id
        cursor.execute("SELECT id FROM posts WHERE url = ?", (post['url'],))
        post_id = cursor.fetchone()['id']
        
        # Calculate individual metric scores from the total score for seeding
        total_score = int(post['score']) * 10 # scale to 100
        # distribute points roughly
        novelty = min(10, int(post['score']))
        virality = min(10, int(post['score']))
        technical_depth = min(10, int(post['score']))
        ai_relevance = min(10, int(post['score']))
        robotics_relevance = 9 if 'robot' in post['text'].lower() else 5
        china_relevance = 9 if post['category'] == 'chinese' else 1
        founder_signal = 9
        research_signal = 8
        
        cursor.execute("""
        INSERT OR REPLACE INTO scores (
            post_id, total_score, novelty, virality, technical_depth, 
            ai_relevance, robotics_relevance, china_relevance, founder_signal, research_signal, reasoning
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            post_id, total_score, novelty, virality, technical_depth, 
            ai_relevance, robotics_relevance, china_relevance, founder_signal, research_signal, 
            post['reasoning']
        ))
        
        if post['comment']:
            cursor.execute("""
            INSERT OR REPLACE INTO generated_comments (post_id, comment_text)
            VALUES (?, ?)
            """, (post_id, post['comment']))
            
    conn.commit()
    conn.close()
    print("[+] Seeding complete!")

if __name__ == "__main__":
    populate_database()
