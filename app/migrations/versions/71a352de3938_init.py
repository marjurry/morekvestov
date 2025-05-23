"""init

Revision ID: 71a352de3938
Revises: 
Create Date: 2025-04-14 12:30:40.661641

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '71a352de3938'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('age_group',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('min_age', sa.Integer(), nullable=False),
    sa.Column('max_age', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user',
    sa.Column('phone_number', sa.BigInteger(), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('phone_number')
    )
    op.create_table('challenge',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('type', sa.String(length=20), nullable=False),
    sa.Column('location_type', sa.String(length=20), nullable=False),
    sa.Column('duration_min', sa.Integer(), nullable=False),
    sa.Column('rules', sa.Text(), nullable=False),
    sa.Column('materials', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('age_group_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['age_group_id'], ['age_group.id'], onupdate='NO ACTION', ondelete='NO ACTION'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('quest',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('total_duration', sa.Integer(), nullable=False),
    sa.Column('location_type', sa.String(length=20), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=True),
    sa.Column('age_group_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['age_group_id'], ['age_group.id'], onupdate='NO ACTION', ondelete='NO ACTION'),
    sa.ForeignKeyConstraint(['user_id'], ['user.phone_number'], onupdate='NO ACTION', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('quest_challenge',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('quest_id', sa.Integer(), nullable=True),
    sa.Column('challenge_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['challenge_id'], ['challenge.id'], onupdate='NO ACTION', ondelete='NO ACTION'),
    sa.ForeignKeyConstraint(['quest_id'], ['quest.id'], onupdate='NO ACTION', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('quest_challenge')
    
    # 2. Удаляем внешние ключи из таблицы Quest
    op.drop_constraint('quest_age_group_id_fkey', 'quest', type_='foreignkey')
    op.drop_constraint('quest_user_id_fkey', 'quest', type_='foreignkey')
    
    # 3. Удаляем таблицу Quest (зависит от User и AgeGroup)
    op.drop_table('quest')
    
    # 4. Удаляем внешние ключи из таблицы Challenge
    op.drop_constraint('challenge_age_group_id_fkey', 'challenge', type_='foreignkey')
    
    # 5. Удаляем таблицу Challenge (зависит от AgeGroup)
    op.drop_table('challenge')
    
    # 6. Удаляем таблицу AgeGroup
    op.drop_table('age_group')
    
    # 7. Удаляем таблицу User (она независимая, можно удалять последней)
    op.drop_table('user')

    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('User',
    sa.Column('phone number', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('password_hash', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('phone number', name='User_pkey'),
    postgresql_ignore_search_path=False
    )

    op.create_table('test',
    sa.Column('num', sa.NUMERIC(precision=6, scale=0), autoincrement=False, nullable=True)
    )
    op.create_table('AgeGroup',
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('min_age', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('max_age', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='AgeGroup_pkey'),
    sa.UniqueConstraint('name', name='AgeGroup_name_key')
    )
    op.create_table('Quest',
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('total_duration', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('location_type', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
    sa.Column('age_group_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['age_group_id'], ['AgeGroup.id'], name='Quest_age_group_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['User.phone number'], name='Quest_user_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='Quest_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('Challenge',
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('title', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('type', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
    sa.Column('location_type', sa.VARCHAR(length=20), autoincrement=False, nullable=False),
    sa.Column('duration_min', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('age_group_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('rules', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('materials', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.CheckConstraint('duration_min > 0', name='Challenge_duration_min_check'),
    sa.ForeignKeyConstraint(['age_group_id'], ['AgeGroup.id'], name='Challenge_age_group_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='Challenge_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('QuestChallenge',
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('quest_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('challenge_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['challenge_id'], ['Challenge.id'], name='QuestChallenge_challenge_id_fkey'),
    sa.ForeignKeyConstraint(['quest_id'], ['Quest.id'], name='QuestChallenge_quest_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='QuestChallenge_pkey')
    )
    op.drop_table('quest_challenge')
    op.drop_table('quest')
    op.drop_table('challenge')
    op.drop_table('user')
    op.drop_table('age_group')
    # ### end Alembic commands ###
