# skills_database.py
"""Database of technical skills and their aliases."""

SKILLS = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "c", "go",
    "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "perl",
    "objective-c", "dart", "elixir", "haskell", "lua", "groovy",
    
    # Web Frontend
    "react", "angular", "vue", "svelte", "ember", "backbone",
    "html", "css", "sass", "less", "scss", "tailwind", "bootstrap",
    "jquery", "webpack", "babel", "redux", "mobx",
    
    # Web Backend
    "django", "flask", "fastapi", "express", "spring", "spring boot",
    "rails", "ruby on rails", "laravel", "symfony", "asp.net",
    "node.js", "next.js", "nuxt.js", "nest.js", "gin", "fiber",
    
    # Mobile
    "react native", "flutter", "android", "ios", "xamarin",
    "ionic", "cordova", "swiftui",
    
    # Databases - SQL
    "mysql", "postgresql", "sqlite", "oracle", "sql server",
    "mariadb", "db2", "sql",
    
    # Databases - NoSQL
    "mongodb", "redis", "cassandra", "couchdb", "neo4j",
    "dynamodb", "firestore", "nosql",
    
    # Search & Analytics
    "elasticsearch", "solr", "splunk", "kibana",
    
    # Cloud Platforms
    "aws", "azure", "gcp", "google cloud", "heroku", "digitalocean",
    "linode", "cloudflare", "vercel", "netlify",
    
    # AWS Services
    "ec2", "s3", "lambda", "rds", "dynamodb", "cloudformation",
    "cloudfront", "route53", "eks", "ecs", "fargate",
    
    # DevOps & CI/CD
    "docker", "kubernetes", "jenkins", "gitlab", "github actions",
    "circleci", "travis ci", "ansible", "terraform", "vagrant",
    "chef", "puppet", "helm", "argocd", "tekton",
    
    # Version Control
    "git", "github", "gitlab", "bitbucket", "svn", "mercurial",
    
    # Data Science & ML
    "pandas", "numpy", "scipy", "scikit-learn", "tensorflow",
    "pytorch", "keras", "xgboost", "lightgbm", "catboost",
    "machine learning", "deep learning", "neural networks",
    "nlp", "computer vision", "data science", "statistics",
    
    # Big Data
    "spark", "hadoop", "kafka", "airflow", "flink", "storm",
    "hive", "pig", "presto", "databricks",
    
    # Testing
    "pytest", "unittest", "jest", "mocha", "chai", "selenium",
    "cypress", "junit", "testng", "jasmine", "karma",
    "tdd", "bdd", "unit testing", "integration testing",
    
    # API & Protocols
    "rest", "graphql", "grpc", "soap", "websocket", "http",
    "tcp/ip", "json", "xml", "yaml", "protobuf",
    
    # Architecture & Patterns
    "microservices", "serverless", "monolith", "event-driven",
    "cqrs", "saga", "mvc", "mvvm", "clean architecture",
    "domain-driven design", "ddd",
    
    # Methodologies
    "agile", "scrum", "kanban", "waterfall", "devops", "devsecops",
    "ci/cd", "continuous integration", "continuous deployment",
    
    # Operating Systems
    "linux", "unix", "ubuntu", "debian", "centos", "redhat",
    "windows", "macos", "bash", "powershell", "shell scripting",
    
    # Containers & Orchestration
    "docker", "kubernetes", "k8s", "openshift", "rancher",
    "docker compose", "docker swarm", "containerd",
    
    # Monitoring & Logging
    "prometheus", "grafana", "datadog", "new relic", "sentry",
    "elk", "elasticsearch", "logstash", "kibana", "splunk",
    
    # Message Queues
    "rabbitmq", "kafka", "redis", "sqs", "sns", "activemq",
    "celery", "zeromq",
    
    # Security
    "oauth", "jwt", "saml", "ssl", "tls", "encryption",
    "penetration testing", "security", "cybersecurity",
    
    # Other Tools
    "jira", "confluence", "slack", "teams", "notion",
    "postman", "insomnia", "swagger", "openapi",
    "vscode", "intellij", "pycharm", "vim", "emacs",
    
    # Concepts
    "oop", "object-oriented programming", "functional programming",
    "data structures", "algorithms", "system design",
    "design patterns", "solid", "dry", "kiss",

    "streamlit", "gradio", "langchain", "huggingface", "transformers",
    "mlflow", "dbt", "snowflake", "bigquery", "looker", "tableau",
    "power bi", "figma", "sketch", "hibernate", "maven", "gradle",
    "cloud computing", "api", "monitoring"
}

SKILL_ALIASES = {
     "tf2": "tensorflow",
    "pt": "pytorch",
    "golang": "go",
    "hf": "huggingface",
    "powerbi": "power bi",
    "aws cloud": "aws",
    "google cloud platform": "gcp",

    # React variations
    "reactjs": "react",
    "react.js": "react",
    
    # Angular variations
    "angularjs": "angular",
    "angular.js": "angular",
    
    # Vue variations
    "vuejs": "vue",
    "vue.js": "vue",
    
    # Node variations
    "nodejs": "node.js",
    "node": "node.js",
    
    # Next.js variations
    "nextjs": "next.js",
    "next": "next.js",
    
    # Database variations
    "postgres": "postgresql",
    "mongo": "mongodb",
    "pgsql": "postgresql",
    
    # Cloud variations
    "amazon web services": "aws",
    "google cloud platform": "gcp",
    "microsoft azure": "azure",
    
    # ML variations
    "ml": "machine learning",
    "dl": "deep learning",
    "ai": "machine learning",
    "sklearn": "scikit-learn",
    "tf": "tensorflow",
    
    # Language variations
    "cpp": "c++",
    "c plus plus": "c++",
    "csharp": "c#",
    "c sharp": "c#",
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    
    # Kubernetes variations
    "k8s": "kubernetes",
    "kube": "kubernetes",
    
    # Container variations
    "containers": "docker",
    
    # Git variations
    "version control": "git",
    
    # Testing variations
    "testing": "unit testing",
    "qa": "unit testing",
    
    # DevOps variations
    "continuous integration": "ci/cd",
    "continuous deployment": "ci/cd",
    
    # API variations
    "rest api": "rest",
    "restful api": "rest",
    "restful": "rest",
    
    # Elasticsearch stack
    "elastic": "elasticsearch",
    "elk stack": "elk",
}