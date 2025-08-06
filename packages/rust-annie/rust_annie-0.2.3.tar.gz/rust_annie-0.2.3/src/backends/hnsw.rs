use hnsw_rs::prelude::*;
use crate::backends::ann_backend::AnnBackend;
use crate::metrics::Distance;
use rust_annie_macros::py_annindex;

/// HNSW backend implementation.
/// For now, only supports Euclidean (L2) distance.
#[py_annindex(backend = "HNSW", distance = "Euclidean")]
pub struct HnswIndex {
    index: Hnsw<'static, f32, DistL2>,
    dims: usize,
}

impl HnswIndex {
    pub fn new(dims: usize, _distance: Distance) -> Self {
        let index = Hnsw::new(
            16,     // M: number of bi-directional links
            10_000, // max elements
            16,     // ef_construction
            200,    // ef_search
            DistL2 {},
        );
        Self { index, dims }
    }
}

impl AnnBackend for HnswIndex {
    fn add(&mut self, vector: Vec<f32>) {
        let id = self.index.get_nb_point();
        self.index.insert((&vector, id));
    }

    fn add_batch(&mut self, vectors: Vec<Vec<f32>>, start_id: usize) {
        // If the underlying index supports batch insertion, use it here for efficiency.
        // Example: self.index.insert_batch(&vectors);
        // If not, consider parallelizing the loop for large batches:
        for (i, v) in vectors.into_iter().enumerate() {
            self.add(v, start_id + i);
        }
    }

    fn remove(&mut self, id: usize) {
        // HNSW doesn't support removal, mark as deleted
        self.deleted.insert(id);
    }

    fn update(&mut self, id: usize, vector: Vec<f32>) {
        if !self.deleted.contains(&id) {
            self.index.remove(id); // Remove old vector
            self.index.insert((&vector, id)); // Add updated vector
            if let Some(v) = self.vectors.get_mut(id) {
                *v = vector;
            }
        }
    }

    fn compact(&mut self) {
        if self.deleted.is_empty() {
            return;
        }
        let mut new_index = Hnsw::new(/* params */);
        for (id, vec) in self.vectors.iter().enumerate() {
            if !self.deleted.contains(&id) {
                new_index.insert((vec, id));
            }
        }
        self.index = new_index;
        self.deleted.clear();
    }

    fn version(&self) -> u64 {
        self.version
    }

    fn search(&self, query: &[f32], k: usize) -> Vec<(usize, f32)> {
        self.index
            .search(query, k, 50)
            .into_iter()
            .map(|n| (n.d_id as usize, n.distance))
            .collect()
    }

    fn len(&self) -> usize {
        self.index.get_nb_point() as usize
    }
}
