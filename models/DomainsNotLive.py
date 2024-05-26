from models.db  import meta
from sqlalchemy import Table, BigInteger, Column, String, Date
from sqlalchemy import Unicode, Boolean, DateTime, UnicodeText, ForeignKey

DomainsNotLiveModel = Table(
    "domain_not_live", meta,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("domain", Unicode(250), nullable=False),
    Column("tanggal", Date, nullable=False),
    Column("cname", Unicode(250), nullable=True),
)