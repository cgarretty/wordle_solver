module wordle_functions
    implicit none
contains
    pure elemental function score_guess(guess, answer) result(score)
        implicit none
        character(len=5), intent(in) :: guess
        character(len=5), intent(in) :: answer
        character(len=5) :: score
        logical, dimension(5) :: ans_char_unsettled
        
        integer :: i ! loop index
        integer :: j ! inner loop index

        ! set vars
        score(:) = " "
        ans_char_unsettled(:) = .true.

        ! set green tiles
        do i = 1, 5
            if (guess(i:i) == answer(i:i)) then
                score(i:i) = "2"
                ans_char_unsettled(i) = .false.
            end if
        end do

        ! set yellow tiles
        do i = 1, 5
            do j = 1, 5
                if (guess(i:i) == answer(j:j) .and. ans_char_unsettled(j) .and. score(i:i) == " ") then
                        score(i:i) = "1"
                        ans_char_unsettled(j) = .false.
                end if
            end do
            ! mark any remaining tiles as gray
            if (score(i:i) == " ") then
                score(i:i) = "0"
            end if
        end do

    end function score_guess
end module wordle_functions
