"""Seed Database of 50 Known AI Startups & Labs with Aliases for Deterministic Entity Resolution."""

KNOWN_AI_STARTUPS = {
    "OpenAI": {
        "canonical": "OpenAI",
        "domain": "openai.com",
        "aliases": ["OpenAI", "OpenAI, Inc.", "Open AI", "OpenAI LLC", "OpenAI Global LLC", "OpenAI Inc"]
    },
    "Anthropic": {
        "canonical": "Anthropic",
        "domain": "anthropic.com",
        "aliases": ["Anthropic", "Anthropic PBC", "Anthropic AI", "Anthropic, Inc.", "Anthropic Inc"]
    },
    "Mistral AI": {
        "canonical": "Mistral AI",
        "domain": "mistral.ai",
        "aliases": ["Mistral", "Mistral AI", "Mistral AI SAS", "Mistral AI, Inc.", "Mistral.ai"]
    },
    "Cohere": {
        "canonical": "Cohere",
        "domain": "cohere.com",
        "aliases": ["Cohere", "Cohere Inc.", "Cohere AI", "Cohere.ai", "Cohere, Inc."]
    },
    "Hugging Face": {
        "canonical": "Hugging Face",
        "domain": "huggingface.co",
        "aliases": ["Hugging Face", "HuggingFace", "Hugging Face, Inc.", "HuggingFace Inc", "Hugging Face Inc."]
    },
    "Scale AI": {
        "canonical": "Scale AI",
        "domain": "scale.com",
        "aliases": ["Scale", "Scale AI", "Scale AI, Inc.", "Scale, Inc.", "ScaleAI"]
    },
    "Perplexity AI": {
        "canonical": "Perplexity AI",
        "domain": "perplexity.ai",
        "aliases": ["Perplexity", "Perplexity AI", "Perplexity, Inc.", "Perplexity AI Inc.", "Perplexity.ai"]
    },
    "Midjourney": {
        "canonical": "Midjourney",
        "domain": "midjourney.com",
        "aliases": ["Midjourney", "Midjourney Inc.", "Midjourney Research", "Midjourney, Inc."]
    },
    "Cursor": {
        "canonical": "Cursor",
        "domain": "cursor.com",
        "aliases": ["Cursor", "Anysphere", "Anysphere Inc.", "Anysphere, Inc.", "Cursor AI"]
    },
    "Databricks": {
        "canonical": "Databricks",
        "domain": "databricks.com",
        "aliases": ["Databricks", "Databricks Inc.", "Databricks, Inc.", "Databricks AI"]
    },
    "xAI": {
        "canonical": "xAI",
        "domain": "x.ai",
        "aliases": ["xAI", "xAI Corp", "x.ai", "X AI", "xAI Corporation"]
    },
    "Runway": {
        "canonical": "Runway",
        "domain": "runwayml.com",
        "aliases": ["Runway", "Runway ML", "Runway AI, Inc.", "RunwayML", "Runway, Inc."]
    },
    "ElevenLabs": {
        "canonical": "ElevenLabs",
        "domain": "elevenlabs.io",
        "aliases": ["ElevenLabs", "Eleven Labs", "ElevenLabs Inc.", "ElevenLabs.io", "Eleven Labs, Inc."]
    },
    "Stability AI": {
        "canonical": "Stability AI",
        "domain": "stability.ai",
        "aliases": ["Stability AI", "Stability.ai", "Stability AI Ltd", "Stability AI Inc.", "StabilityAI"]
    },
    "Jasper AI": {
        "canonical": "Jasper AI",
        "domain": "jasper.ai",
        "aliases": ["Jasper", "Jasper AI", "Jasper.ai", "Jasper Technologies Inc.", "Jasper AI, Inc."]
    },
    "Character.ai": {
        "canonical": "Character.ai",
        "domain": "character.ai",
        "aliases": ["Character.ai", "Character AI", "Character Technologies Inc.", "Character AI, Inc."]
    },
    "Glean": {
        "canonical": "Glean",
        "domain": "glean.com",
        "aliases": ["Glean", "Glean Technologies Inc.", "Glean Search", "Glean, Inc."]
    },
    "Harvey": {
        "canonical": "Harvey",
        "domain": "harvey.ai",
        "aliases": ["Harvey", "Harvey AI", "Harvey Technologies, Inc.", "Harvey, Inc."]
    },
    "Adept": {
        "canonical": "Adept",
        "domain": "adept.ai",
        "aliases": ["Adept", "Adept AI", "Adept AI Labs, Inc.", "Adept Labs"]
    },
    "Together AI": {
        "canonical": "Together AI",
        "domain": "together.ai",
        "aliases": ["Together", "Together AI", "Together Computer Inc.", "Together.ai", "Together AI, Inc."]
    },
    "Replicate": {
        "canonical": "Replicate",
        "domain": "replicate.com",
        "aliases": ["Replicate", "Replicate Inc.", "Replicate.com", "Replicate, Inc."]
    },
    "DeepL": {
        "canonical": "DeepL",
        "domain": "deepl.com",
        "aliases": ["DeepL", "DeepL SE", "DeepL GmbH", "DeepL Translator"]
    },
    "Pinecone": {
        "canonical": "Pinecone",
        "domain": "pinecone.io",
        "aliases": ["Pinecone", "Pinecone Systems Inc.", "Pinecone.io", "Pinecone Systems, Inc."]
    },
    "Qdrant": {
        "canonical": "Qdrant",
        "domain": "qdrant.tech",
        "aliases": ["Qdrant", "Qdrant Solutions GmbH", "Qdrant.tech"]
    },
    "Weaviate": {
        "canonical": "Weaviate",
        "domain": "weaviate.io",
        "aliases": ["Weaviate", "Weaviate B.V.", "SeMI Technologies B.V.", "Weaviate.io"]
    },
    "Chroma": {
        "canonical": "Chroma",
        "domain": "trychroma.com",
        "aliases": ["Chroma", "Chroma DB", "Chroma Inc.", "Chroma, Inc."]
    },
    "LangChain": {
        "canonical": "LangChain",
        "domain": "langchain.com",
        "aliases": ["LangChain", "LangChain Inc.", "LangChain.ai", "LangChain, Inc."]
    },
    "LlamaIndex": {
        "canonical": "LlamaIndex",
        "domain": "llamaindex.ai",
        "aliases": ["LlamaIndex", "LlamaIndex Inc.", "Jerry AI Inc.", "Run Llama"]
    },
    "Weights & Biases": {
        "canonical": "Weights & Biases",
        "domain": "wandb.ai",
        "aliases": ["Weights & Biases", "W&B", "Weights and Biases", "Weights & Biases Inc.", "Wandb"]
    },
    "Snorkel AI": {
        "canonical": "Snorkel AI",
        "domain": "snorkel.ai",
        "aliases": ["Snorkel", "Snorkel AI", "Snorkel AI, Inc.", "Snorkel, Inc."]
    },
    "Synthesia": {
        "canonical": "Synthesia",
        "domain": "synthesia.io",
        "aliases": ["Synthesia", "Synthesia Limited", "Synthesia Ltd", "Synthesia.io"]
    },
    "HeyGen": {
        "canonical": "HeyGen",
        "domain": "heygen.com",
        "aliases": ["HeyGen", "HeyGen Inc.", "HeyGen AI", "HeyGen, Inc."]
    },
    "Pika": {
        "canonical": "Pika",
        "domain": "pika.art",
        "aliases": ["Pika", "Pika Labs", "Pika Art", "Pika Labs Inc.", "Pika, Inc."]
    },
    "Suno": {
        "canonical": "Suno",
        "domain": "suno.com",
        "aliases": ["Suno", "Suno AI", "Suno, Inc.", "Suno Inc"]
    },
    "Udio": {
        "canonical": "Udio",
        "domain": "udio.com",
        "aliases": ["Udio", "Udio AI", "Uncharted Labs Inc.", "Uncharted Labs"]
    },
    "Writer": {
        "canonical": "Writer",
        "domain": "writer.com",
        "aliases": ["Writer", "Writer Inc.", "Writer.com", "Writer AI"]
    },
    "Contextual AI": {
        "canonical": "Contextual AI",
        "domain": "contextual.ai",
        "aliases": ["Contextual AI", "Contextual AI Inc.", "Contextual"]
    },
    "Inflection AI": {
        "canonical": "Inflection AI",
        "domain": "inflection.ai",
        "aliases": ["Inflection", "Inflection AI", "Inflection AI, Inc.", "Inflection AI Inc"]
    },
    "Covariant": {
        "canonical": "Covariant",
        "domain": "covariant.ai",
        "aliases": ["Covariant", "Covariant.ai", "Covariant Inc.", "Covariant, Inc."]
    },
    "Figure AI": {
        "canonical": "Figure AI",
        "domain": "figure.ai",
        "aliases": ["Figure", "Figure AI", "Figure AI, Inc.", "Figure AI Inc"]
    },
    "Physical Intelligence": {
        "canonical": "Physical Intelligence",
        "domain": "physicalintelligence.company",
        "aliases": ["Physical Intelligence", "Pi", "Physical Intelligence Inc.", "Physical Intelligence, Inc."]
    },
    "Sakana AI": {
        "canonical": "Sakana AI",
        "domain": "sakana.ai",
        "aliases": ["Sakana", "Sakana AI", "Sakana AI Inc.", "Sakana AI, Inc."]
    },
    "Cognition": {
        "canonical": "Cognition",
        "domain": "cognition.ai",
        "aliases": ["Cognition", "Cognition AI", "Cognition Labs Inc.", "Cognition Labs", "Devin AI"]
    },
    "Poolside": {
        "canonical": "Poolside",
        "domain": "poolside.ai",
        "aliases": ["Poolside", "Poolside AI", "Poolside SAS", "Poolside AI, Inc."]
    },
    "EvolutionaryScale": {
        "canonical": "EvolutionaryScale",
        "domain": "evolutionaryscale.ai",
        "aliases": ["EvolutionaryScale", "EvoScale", "EvolutionaryScale Inc.", "EvolutionaryScale, Inc."]
    },
    "Decagon": {
        "canonical": "Decagon",
        "domain": "decagon.ai",
        "aliases": ["Decagon", "Decagon AI", "Decagon Inc.", "Decagon, Inc."]
    },
    "Sierra": {
        "canonical": "Sierra",
        "domain": "sierra.ai",
        "aliases": ["Sierra", "Sierra Technologies Inc.", "Sierra AI", "Sierra, Inc."]
    },
    "Baseten": {
        "canonical": "Baseten",
        "domain": "baseten.co",
        "aliases": ["Baseten", "Baseten Inc.", "Baseten Labs", "Baseten, Inc."]
    },
    "Modal": {
        "canonical": "Modal",
        "domain": "modal.com",
        "aliases": ["Modal", "Modal Labs", "Modal Labs Inc.", "Modal Labs, Inc."]
    },
    "Fireworks AI": {
        "canonical": "Fireworks AI",
        "domain": "fireworks.ai",
        "aliases": ["Fireworks", "Fireworks AI", "Fireworks AI Inc.", "Fireworks AI, Inc."]
    }
}
