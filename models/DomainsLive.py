from models.db import meta
from sqlalchemy import Table, BigInteger, Column, String, Date
from sqlalchemy import Unicode, Boolean, DateTime, UnicodeText, ForeignKey

DomainsModel = Table(
    "domain_live", meta,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("domain", Unicode(250), nullable=False),
    Column("tanggal", Date, nullable=False),
    Column("cname", Unicode(250), nullable=True),
    Column("scanned", Boolean, nullable=True),
    Column("vuln", Unicode(250), nullable=True),
)