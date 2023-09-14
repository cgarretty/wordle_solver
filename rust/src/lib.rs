use polars::prelude::*;
use std::collections::HashMap;
use pyo3::prelude::*;
use pyo3_polars::PyDataFrame;

const GREEN: u8 = 2;
const YELLOW: u8 = 1;
const GRAY: u8 = 0;

#[pyfunction]
fn score_guess(answer: &str, guess: &str) -> String {
    let mut score: [u8; 5] = [GRAY; 5];
    let mut settled_answer_letters = [false; 5];

    for (i, (a, g)) in guess.chars().zip(answer.chars()).enumerate() {
        if a == g {
            score[i] = GREEN;
            settled_answer_letters[i] = true;
        }
    }

    for (i, letter) in guess.chars().enumerate() {
        if let Some(found_index) = answer.chars().zip(settled_answer_letters).position(|c| c.0 == letter && !c.1) {
            if score[i] != GREEN {
                score[i] = YELLOW;
                settled_answer_letters[found_index] = true ;
            }
        }
    }
    
    //convert to string
    let score_string: String = score.iter().map(|&x| x.to_string()).collect();
    
    return score_string;
    
}

#[pyfunction]
fn score_all_words(answers: Vec<&str>, guesses: Vec<&str>) -> PyResult<PyDataFrame> {    
    let mut df = DataFrame::default();
    
    for answer in answers.iter() {
        let scores: Vec<String> = guesses.iter().map(|guess| score_guess(&answer, &guess)).collect();
        df.with_column(Series::new(answer, scores)).unwrap();
    }

    return Ok(PyDataFrame(df));
}

#[pyfunction]
fn highest_count_of_unique_arrays(vectors: Vec<Vec<u8>>) -> usize {
    let mut unique_arrays = HashMap::new();
    let mut max_count = 0;
    for vector in vectors {
        let count = unique_arrays.entry(vector).or_insert(0);
        *count += 1;
        if *count > max_count {
            max_count = *count;
        }
    }
    
    return max_count;
}


/// A Python module implemented in Rust.
#[pymodule]
fn rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(score_guess, m)?)?;
    m.add_function(wrap_pyfunction!(score_all_words, m)?)?;
    m.add_function(wrap_pyfunction!(highest_count_of_unique_arrays, m)?)?;
    Ok(())
}

