use pyo3::prelude::*;
use pyo3::types::{IntoPyDict, PyDict};
use pyo3::ToPyObject;


const GREEN: u8 = 2;
const YELLOW: u8 = 1;
const GRAY: u8 = 0;

#[pyfunction]
fn score_guess(answer: &str, guess: &str) -> [u8; 5] {
    let mut score: [u8; 5] = [GRAY; 5];
    let answer_chars = answer.as_bytes();
    let guess_chars = guess.as_bytes();
    let mut settled_letters = [false; 5];

    for i in 0..5 {
        if answer_chars[i] == guess_chars[i] {
            score[i] = GREEN;
            settled_letters[i] = true;
        } 
    }

    for i in 0..5 {
        if !settled_letters[i] { 
            if let Some(found_index) = answer_chars.iter().enumerate()
                .find(|(j, &c)| !settled_letters[*j] && c == guess_chars[i]) {
                    let (found_index, _) = found_index;
                    score[i] = YELLOW;
                    settled_letters[found_index] = true;
            } 
        }
    }

    return score
}

#[pyfunction]
fn score_all_words(py: Python, answers: Vec<String>, guesses: Vec<String>) -> PyResult<Py<PyDict>> {    
    let mut score_card = vec![];
    let mut scores = vec![];

    for guess in guesses.iter() {
        scores.clear();
        scores = answers.iter().map(|answer| score_guess(&answer, &guess).to_vec()).collect();
        score_card.push((guess, ToPyObject::to_object(&scores, py)));
    }

    let locals = score_card.into_py_dict(py);

    Ok(locals.into())
}

#[pyfunction]
fn filter_words(guess_result: Vec<u8>, possible_solutions: Vec<bool>, score_card: Vec<Vec<u8>>) -> Vec<bool> {
    let mut possible_solutions_copy = possible_solutions.to_vec();
    
    for (i, score) in score_card.iter().enumerate() {
        if do_vecs_match(score, &guess_result) {
            possible_solutions_copy[i] = false;
        }
    }
    possible_solutions_copy
}

fn do_vecs_match<T: PartialEq>(a: &Vec<T>, b: &Vec<T>) -> bool {
    let matching = a.iter().zip(b.iter()).filter(|&(a, b)| a == b).count();
    matching == a.len() && matching == b.len()
}

/// A Python module implemented in Rust.
#[pymodule]
fn rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(score_guess, m)?)?;
    m.add_function(wrap_pyfunction!(score_all_words, m)?)?;
    m.add_function(wrap_pyfunction!(filter_words, m)?)?;
    Ok(())
}

