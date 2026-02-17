"""initial_migration

Revision ID: 001
Revises: 
Create Date: 2024-02-17 11:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables for the AI Interview Platform."""
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    # Create interviews table
    op.create_table(
        'interviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interviews_id'), 'interviews', ['id'], unique=False)
    op.create_index(op.f('ix_interviews_user_id'), 'interviews', ['user_id'], unique=False)
    op.create_index(op.f('ix_interviews_created_at'), 'interviews', ['created_at'], unique=False)
    
    # Create questions table
    op.create_table(
        'questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('interview_id', sa.Integer(), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('question_order', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['interview_id'], ['interviews.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_questions_id'), 'questions', ['id'], unique=False)
    op.create_index(op.f('ix_questions_interview_id'), 'questions', ['interview_id'], unique=False)
    
    # Create answers table
    op.create_table(
        'answers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('answer_text', sa.Text(), nullable=False),
        sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_answers_id'), 'answers', ['id'], unique=False)
    op.create_index(op.f('ix_answers_question_id'), 'answers', ['question_id'], unique=False)
    op.create_index(op.f('ix_answers_user_id'), 'answers', ['user_id'], unique=False)
    
    # Create evaluations table
    op.create_table(
        'evaluations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('answer_id', sa.Integer(), nullable=False),
        sa.Column('scores', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('feedback', sa.Text(), nullable=False),
        sa.Column('suggestions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('evaluated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.ForeignKeyConstraint(['answer_id'], ['answers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('answer_id')
    )
    op.create_index(op.f('ix_evaluations_id'), 'evaluations', ['id'], unique=False)
    op.create_index(op.f('ix_evaluations_answer_id'), 'evaluations', ['answer_id'], unique=True)
    op.create_index(op.f('ix_evaluations_status'), 'evaluations', ['status'], unique=False)


def downgrade() -> None:
    """Drop all tables in reverse order."""
    
    # Drop tables in reverse order to respect foreign key constraints
    op.drop_index(op.f('ix_evaluations_status'), table_name='evaluations')
    op.drop_index(op.f('ix_evaluations_answer_id'), table_name='evaluations')
    op.drop_index(op.f('ix_evaluations_id'), table_name='evaluations')
    op.drop_table('evaluations')
    
    op.drop_index(op.f('ix_answers_user_id'), table_name='answers')
    op.drop_index(op.f('ix_answers_question_id'), table_name='answers')
    op.drop_index(op.f('ix_answers_id'), table_name='answers')
    op.drop_table('answers')
    
    op.drop_index(op.f('ix_questions_interview_id'), table_name='questions')
    op.drop_index(op.f('ix_questions_id'), table_name='questions')
    op.drop_table('questions')
    
    op.drop_index(op.f('ix_interviews_created_at'), table_name='interviews')
    op.drop_index(op.f('ix_interviews_user_id'), table_name='interviews')
    op.drop_index(op.f('ix_interviews_id'), table_name='interviews')
    op.drop_table('interviews')
    
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
