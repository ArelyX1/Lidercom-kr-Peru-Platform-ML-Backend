Requeriments:
REDIS - CELERY queue & processing - Rust
ML processing module - Python
GraphQL - IDK xd i would use Rust and Python
I need make Certificates - blockchain?
Aproach the DB processing - Timescale
Account security - Rust

Independent Modules:
ML
QUEUE
LIDERCOM-APIS
ACCOUNT SIGN UP
CERTIFICATES

Now for backend i need add this: Blockchain wallets for share info about accounts, like:

El padre entra a la app (Login tradicional).

Tu backend mira la tabla Relacion_Familiar y confirma: "Sí, este UUID es el padre de este otro UUID".

Aquí viene el truco: El backend toma la wallet_address del padre y la del hijo y le pregunta a la Blockchain: "Dame los registros firmados para la wallet 0xHijo que la wallet 0xPadre tiene permiso de ver".

I mean the superior account can see the transactions that participant has been realized.
