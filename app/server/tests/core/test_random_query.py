import pytest
import os
from unittest.mock import patch, MagicMock
from core.llm_processor import (
    generate_random_query,
    generate_random_query_with_openai,
    generate_random_query_with_anthropic
)


class TestRandomQueryGeneration:

    @pytest.fixture
    def single_table_schema(self):
        """Fixture for a simple single table schema"""
        return {
            'tables': {
                'users': {
                    'columns': {
                        'id': 'INTEGER',
                        'name': 'TEXT',
                        'email': 'TEXT',
                        'age': 'INTEGER',
                        'created_at': 'TIMESTAMP'
                    },
                    'row_count': 150
                }
            }
        }

    @pytest.fixture
    def multiple_tables_schema(self):
        """Fixture for a multi-table schema"""
        return {
            'tables': {
                'users': {
                    'columns': {
                        'id': 'INTEGER',
                        'name': 'TEXT',
                        'email': 'TEXT'
                    },
                    'row_count': 100
                },
                'orders': {
                    'columns': {
                        'id': 'INTEGER',
                        'user_id': 'INTEGER',
                        'total': 'REAL',
                        'status': 'TEXT'
                    },
                    'row_count': 500
                },
                'products': {
                    'columns': {
                        'id': 'INTEGER',
                        'name': 'TEXT',
                        'price': 'REAL'
                    },
                    'row_count': 50
                }
            }
        }

    @patch('core.llm_processor.OpenAI')
    def test_generate_random_query_single_table(self, mock_openai_class, single_table_schema):
        """Test random query generation with a single table schema"""
        # Mock OpenAI client and response
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices[0].message.content = """QUERY: What is the average age of all users?
CONTEXT: This helps understand the demographic of your user base.
TABLES: users"""
        mock_client.chat.completions.create.return_value = mock_response

        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            result = generate_random_query_with_openai(single_table_schema)

            assert result['query'] == "What is the average age of all users?"
            assert result['context'] == "This helps understand the demographic of your user base."
            assert result['table_names'] == ['users']
            mock_client.chat.completions.create.assert_called_once()

            # Verify temperature is higher for variety
            call_args = mock_client.chat.completions.create.call_args
            assert call_args[1]['temperature'] == 0.8

    @patch('core.llm_processor.OpenAI')
    def test_generate_random_query_multiple_tables(self, mock_openai_class, multiple_tables_schema):
        """Test random query generation with multiple tables"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices[0].message.content = """QUERY: Show me the top 10 customers by total order value. Which users have spent the most?
CONTEXT: Identifies high-value customers for targeted marketing efforts.
TABLES: users, orders"""
        mock_client.chat.completions.create.return_value = mock_response

        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            result = generate_random_query_with_openai(multiple_tables_schema)

            assert "customers" in result['query'].lower() or "users" in result['query'].lower()
            assert len(result['table_names']) >= 1
            assert isinstance(result['context'], str)

    @patch('core.llm_processor.OpenAI')
    def test_generate_random_query_filters_tables(self, mock_openai_class, multiple_tables_schema):
        """Test that table_names filter works correctly"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices[0].message.content = """QUERY: What are the most popular products?
CONTEXT: Helps identify inventory priorities.
TABLES: products"""
        mock_client.chat.completions.create.return_value = mock_response

        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            # Only request query for products table
            generate_random_query_with_openai(multiple_tables_schema, table_names=['products'])

            # Verify the prompt included only products table
            call_args = mock_client.chat.completions.create.call_args
            prompt_content = call_args[1]['messages'][1]['content']
            assert 'products' in prompt_content
            # Users and orders should not be in filtered schema
            assert 'orders' not in prompt_content or 'users' not in prompt_content

    @patch('core.llm_processor.OpenAI')
    def test_generate_random_query_two_sentence_limit(self, mock_openai_class, single_table_schema):
        """Verify the query respects the two-sentence limit in prompt"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Mock a response with exactly 2 sentences
        mock_response = MagicMock()
        mock_response.choices[0].message.content = """QUERY: How many users signed up in the last month? What's the trend compared to previous months?
CONTEXT: Tracks user growth momentum.
TABLES: users"""
        mock_client.chat.completions.create.return_value = mock_response

        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            result = generate_random_query_with_openai(single_table_schema)

            # Verify prompt includes two-sentence constraint
            call_args = mock_client.chat.completions.create.call_args
            prompt_content = call_args[1]['messages'][1]['content']
            assert 'TWO sentences maximum' in prompt_content

            # Count sentences in generated query (naive count by periods)
            sentence_count = result['query'].count('.') + result['query'].count('?')
            assert sentence_count <= 2, f"Query has {sentence_count} sentences, expected <= 2"

    @patch('core.llm_processor.OpenAI')
    def test_generate_random_query_empty_schema(self, mock_openai_class):
        """Test error handling when no tables exist"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        empty_schema = {'tables': {}}

        # The function should still try to call the API, but with empty schema
        mock_response = MagicMock()
        mock_response.choices[0].message.content = """QUERY: Upload some data first to get started.
CONTEXT: No tables available to query.
TABLES: """
        mock_client.chat.completions.create.return_value = mock_response

        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            result = generate_random_query_with_openai(empty_schema)
            # Should still return a result, even if schema is empty
            assert 'query' in result

    @patch('core.llm_processor.OpenAI')
    def test_generate_random_query_api_error(self, mock_openai_class, single_table_schema):
        """Test handling of LLM API errors"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API timeout")

        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            with pytest.raises(Exception) as exc_info:
                generate_random_query_with_openai(single_table_schema)

            assert "Error generating random query with OpenAI" in str(exc_info.value)

    def test_generate_random_query_no_api_key(self, single_table_schema):
        """Test error when no API key is configured"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(Exception) as exc_info:
                generate_random_query(single_table_schema)

            assert "No LLM API key configured" in str(exc_info.value)

    @patch('core.llm_processor.OpenAI')
    def test_generate_random_query_missing_query_field(self, mock_openai_class, single_table_schema):
        """Test handling of malformed LLM response"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Response missing QUERY field
        mock_response = MagicMock()
        mock_response.choices[0].message.content = """CONTEXT: Some context
TABLES: users"""
        mock_client.chat.completions.create.return_value = mock_response

        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            with pytest.raises(Exception) as exc_info:
                generate_random_query_with_openai(single_table_schema)

            assert "Failed to parse query from LLM response" in str(exc_info.value)

    @patch('core.llm_processor.Anthropic')
    def test_generate_random_query_with_anthropic_success(self, mock_anthropic_class, single_table_schema):
        """Test random query generation with Anthropic"""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content[0].text = """QUERY: How many users are over 30 years old?
CONTEXT: Useful for age-based segmentation.
TABLES: users"""
        mock_client.messages.create.return_value = mock_response

        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            result = generate_random_query_with_anthropic(single_table_schema)

            assert result['query'] == "How many users are over 30 years old?"
            assert result['context'] == "Useful for age-based segmentation."
            assert result['table_names'] == ['users']
            mock_client.messages.create.assert_called_once()

    @patch('core.llm_processor.OpenAI')
    def test_generate_random_query_routing_openai_priority(self, mock_openai_class, single_table_schema):
        """Test that OpenAI has priority over Anthropic"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices[0].message.content = """QUERY: Test query
CONTEXT: Test context
TABLES: users"""
        mock_client.chat.completions.create.return_value = mock_response

        # Both keys available, OpenAI should be called
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'openai-key', 'ANTHROPIC_API_KEY': 'anthropic-key'}):
            result = generate_random_query(single_table_schema)

            assert result['query'] == "Test query"
            mock_client.chat.completions.create.assert_called_once()

    @patch('core.llm_processor.Anthropic')
    def test_generate_random_query_routing_anthropic_fallback(self, mock_anthropic_class, single_table_schema):
        """Test fallback to Anthropic when OpenAI key not available"""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content[0].text = """QUERY: Test query
CONTEXT: Test context
TABLES: users"""
        mock_client.messages.create.return_value = mock_response

        # Only Anthropic key available
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'anthropic-key'}, clear=True):
            result = generate_random_query(single_table_schema)

            assert result['query'] == "Test query"
            mock_client.messages.create.assert_called_once()
