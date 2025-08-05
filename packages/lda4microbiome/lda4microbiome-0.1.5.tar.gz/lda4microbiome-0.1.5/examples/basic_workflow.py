#!/usr/bin/env python3
"""
Basic LDA4Microbiome workflow example

This script demonstrates how to use the LDA4Microbiome package
for a complete microbiome LDA analysis workflow.
"""

from lda4microbiome import TaxonomyProcessor, LDATrainer, SankeyDataProcessor, LDAModelVisualizer

def main():
    # Configuration
    base_directory = 'example_analysis'
    asvtable_path = 'data/sample_table.csv'
    taxonomy_path = 'data/taxonomy.csv'
    metadata_path = 'data/metadata.csv'
    path_to_mallet = 'path/to/mallet/bin/mallet'
    
    # Step 1: Preprocess taxonomic data
    print("Step 1: Processing taxonomic data...")
    processor = TaxonomyProcessor(
        asvtable_path=asvtable_path,
        taxonomy_path=taxonomy_path,
        base_directory=base_directory
    )
    results = processor.process_all()
    
    # Step 2: Train LDA models
    print("Step 2: Training LDA models...")
    trainer = LDATrainer(
        base_directory=base_directory,
        path_to_mallet=path_to_mallet
    )
    MC_range = list(range(2, 11))  # Test 2-10 topics
    lda_results = trainer.train_models(MC_range)
    
    # Step 3: Process results for model selection
    print("Step 3: Processing results for model selection...")
    sankey_processor = SankeyDataProcessor.from_lda_trainer(trainer)
    sankey_data = sankey_processor.process_all_data()
    
    # Step 4: Create visualizations for selected model
    print("Step 4: Creating visualizations...")
    selected_k = 5  # Choose based on model selection results
    visualizer = LDAModelVisualizer(
        base_directory=base_directory,
        k_value=selected_k,
        metadata_path=metadata_path,
        universal_headers=["Group", "Batch"],
        continuous_headers=["Age", "BMI"]
    )
    plots = visualizer.create_all_visualizations()
    
    print("Analysis complete!")

if __name__ == "__main__":
    main()

