import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import os

# Import the class to be tested
from lda4microbiome.3_selection import SankeyDataProcessor

class TestSankeyDataProcessor(unittest.TestCase):

    def setUp(self):
        """Set up a mock environment for testing."""
        self.base_directory = '/tmp/test_sankey_processor'
        self.MC_range = [2, 3, 4]
        self.range_str = '2-4'
        
        # Create mock directories and files
        os.makedirs(os.path.join(self.base_directory, 'lda_results', 'MC_Sample'), exist_ok=True)
        os.makedirs(os.path.join(self.base_directory, 'lda_results', 'MC_Feature'), exist_ok=True)
        
        # Mock sample probability files
        for k in self.MC_range:
            sample_prob_df = pd.DataFrame({
                'sample1': [0.8, 0.2] if k == 2 else [0.7, 0.2, 0.1] if k == 3 else [0.6, 0.2, 0.1, 0.1],
                'sample2': [0.3, 0.7] if k == 2 else [0.1, 0.8, 0.1] if k == 3 else [0.1, 0.7, 0.1, 0.1],
            }, index=[f'K{k}_MC{i}' for i in range(k)])
            sample_prob_df.to_csv(os.path.join(self.base_directory, 'lda_results', 'MC_Sample', f'MC_Sample_probabilities{k}.csv'))
        
        # Mock comprehensive metrics file
        metrics_df = pd.DataFrame({
            'Topic_Name': ['K2_MC0', 'K2_MC1', 'K3_MC0', 'K3_MC1', 'K3_MC2'],
            'K': [2, 2, 3, 3, 3],
            'Perplexity': [150.0, 150.0, 120.0, 120.0, 120.0],
            'Coherence': [-1.5, -2.0, -1.2, -1.8, -2.5]
        })
        metrics_df.to_csv(os.path.join(self.base_directory, 'lda_results', f'comprehensive_MC_metrics_{self.range_str}.csv'), index=False)

    def test_load_metrics_from_comprehensive_file(self):
        """Test loading metrics from the comprehensive CSV file."""
        processor = SankeyDataProcessor(
            base_directory=self.base_directory,
            MC_range=self.MC_range
        )
        
        metrics_data = processor.load_metrics_data()
        
        self.assertIn('K2_MC0', metrics_data)
        self.assertIn('K3_MC1', metrics_data)
        self.assertEqual(metrics_data['K2_MC0']['perplexity'], 150.0)
        self.assertEqual(metrics_data['K3_MC1']['coherence'], -1.8)

    def test_process_data_with_comprehensive_metrics(self):
        """Test the full data processing pipeline with comprehensive metrics."""
        processor = SankeyDataProcessor(
            base_directory=self.base_directory,
            MC_range=self.MC_range
        )
        
        sankey_data = processor.process_all_data()
        
        self.assertIn('K2_MC0', sankey_data['nodes'])
        self.assertIn('model_metrics', sankey_data['nodes']['K2_MC0'])
        self.assertEqual(sankey_data['nodes']['K2_MC0']['model_metrics']['perplexity'], 150.0)
        self.assertEqual(sankey_data['nodes']['K2_MC1']['model_metrics']['coherence'], -2.0)

if __name__ == '__main__':
    unittest.main()

