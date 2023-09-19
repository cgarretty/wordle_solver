function score_guesses(guesses, answers) result(scores)
    use wordle_functions
    implicit none

    character(len=5), dimension(:), intent(in) :: guesses, answers
    character(len=5), dimension(size(guesses), size(answers)) :: scores
    integer :: i
    integer :: j
    integer :: answer_size
    integer :: guess_size

    answer_size = size(answers)
    guess_size = size(guesses)

    do i = 1, guess_size
        do j = 1, answer_size
            scores(i, j) = score_guess(guesses(i), answers(j))
        end do
    end do

end function score_guesses
