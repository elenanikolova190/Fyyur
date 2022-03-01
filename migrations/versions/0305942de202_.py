"""empty message

Revision ID: 0305942de202
Revises: ab689bcb3664
Create Date: 2022-02-28 11:59:11.078656

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0305942de202'
down_revision = 'ab689bcb3664'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('artist_genres')
    op.drop_table('venue')
    op.drop_table('shows')
    op.drop_table('artist')
    op.drop_table('venue_genres')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('venue_genres',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('venue_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('genre', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['venue_id'], ['venue.id'], name='venue_genres_venue_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='venue_genres_pkey')
    )
    op.create_table('artist',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('artist_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('city', sa.VARCHAR(length=120), autoincrement=False, nullable=False),
    sa.Column('state', sa.VARCHAR(length=120), autoincrement=False, nullable=False),
    sa.Column('phone', sa.VARCHAR(length=120), autoincrement=False, nullable=False),
    sa.Column('image_link', sa.VARCHAR(length=500), autoincrement=False, nullable=True),
    sa.Column('facebook_link', sa.VARCHAR(length=120), autoincrement=False, nullable=True),
    sa.Column('seeking_venue', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('seeking_description', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='artist_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('shows',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('venue_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('artist_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('start_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['artist.id'], name='shows_artist_id_fkey'),
    sa.ForeignKeyConstraint(['venue_id'], ['venue.id'], name='shows_venue_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='shows_pkey')
    )
    op.create_table('venue',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('city', sa.VARCHAR(length=120), autoincrement=False, nullable=False),
    sa.Column('state', sa.VARCHAR(length=120), autoincrement=False, nullable=False),
    sa.Column('address', sa.VARCHAR(length=120), autoincrement=False, nullable=False),
    sa.Column('phone', sa.VARCHAR(length=120), autoincrement=False, nullable=False),
    sa.Column('image_link', sa.VARCHAR(length=500), autoincrement=False, nullable=True),
    sa.Column('facebook_link', sa.VARCHAR(length=120), autoincrement=False, nullable=True),
    sa.Column('seeking_talent', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('seeking_description', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('website_link', sa.VARCHAR(length=300), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='venue_pkey')
    )
    op.create_table('artist_genres',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('artist_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('genre', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['artist.id'], name='artist_genres_artist_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='artist_genres_pkey')
    )
    # ### end Alembic commands ###
