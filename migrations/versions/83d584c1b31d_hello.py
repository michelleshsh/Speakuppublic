"""hello

Revision ID: 83d584c1b31d
Revises: 
Create Date: 2020-09-02 13:56:19.403197

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '83d584c1b31d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('hansard',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.String(length=140), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('about_me', sa.String(length=140), nullable=True),
    sa.Column('representative', sa.String(length=100), nullable=True),
    sa.Column('constituency', sa.String(length=100), nullable=True),
    sa.Column('postcode', sa.String(length=64), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('followers',
    sa.Column('follower_id', sa.Integer(), nullable=True),
    sa.Column('followed_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], )
    )
    op.create_table('majorheading',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('hansard_id', sa.Integer(), nullable=True),
    sa.Column('body', sa.String(length=300), nullable=True),
    sa.ForeignKeyConstraint(['hansard_id'], ['hansard.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_majorheading_order_id'), 'majorheading', ['order_id'], unique=False)
    op.create_table('post',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.String(length=140), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_post_timestamp'), 'post', ['timestamp'], unique=False)
    op.create_table('minorheading',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('major_id', sa.Integer(), nullable=True),
    sa.Column('body', sa.String(length=140), nullable=True),
    sa.ForeignKeyConstraint(['major_id'], ['majorheading.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_minorheading_order_id'), 'minorheading', ['order_id'], unique=False)
    op.create_table('speech',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('minor_id', sa.Integer(), nullable=True),
    sa.Column('exact_id', sa.String(length=140), nullable=True),
    sa.Column('author_id', sa.String(length=140), nullable=True),
    sa.ForeignKeyConstraint(['minor_id'], ['minorheading.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_speech_order_id'), 'speech', ['order_id'], unique=False)
    op.create_table('paragraph',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('speech_id', sa.Integer(), nullable=True),
    sa.Column('body', sa.String(length=10000), nullable=True),
    sa.ForeignKeyConstraint(['speech_id'], ['speech.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_paragraph_order_id'), 'paragraph', ['order_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_paragraph_order_id'), table_name='paragraph')
    op.drop_table('paragraph')
    op.drop_index(op.f('ix_speech_order_id'), table_name='speech')
    op.drop_table('speech')
    op.drop_index(op.f('ix_minorheading_order_id'), table_name='minorheading')
    op.drop_table('minorheading')
    op.drop_index(op.f('ix_post_timestamp'), table_name='post')
    op.drop_table('post')
    op.drop_index(op.f('ix_majorheading_order_id'), table_name='majorheading')
    op.drop_table('majorheading')
    op.drop_table('followers')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_table('hansard')
    # ### end Alembic commands ###
