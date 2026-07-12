┌─────────────────────────────────────────────────────────────┐
│                        Docker Network                        │
│                                                              │
│  ┌──────────────┐    push task    ┌──────────────────────┐  │
│  │   FastAPI    │ ─────────────► │   Redis              │  │
│  │   Container  │                │   Container           │  │
│  │              │ ◄───────────── │                      │  │
│  │  .delay()    │  cache get/set │  • Celery queue      │  │
│  │  redis.get() │                │  • Cache storage     │  │
│  │  redis.set() │                │  • Task results      │  │
│  └──────────────┘                └──────────────────────┘  │
│                                          │  pop task         │
│                                          ▼                   │
│                                  ┌──────────────────────┐   │
│                                  │   Celery Worker      │   │
│                                  │   Container          │   │
│                                  │                      │   │
│                                  │  send_email()        │   │
│                                  │  process_refund()    │   │
│                                  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────┘