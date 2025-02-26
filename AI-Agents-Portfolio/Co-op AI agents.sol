// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title SavingsGroup
 * @dev A smart contract for WashikaDAO savings groups that allows members to:
 *      - Purchase shares
 *      - Allocate a percentage of funds to savings
 *      - Apply for a loan based on shareholding
 *      - Repay loans before borrowing again
 */
contract SavingsGroup {
    // Structure to store details of each member
    struct Member {
        uint256 shares; // Number of shares owned by the member
        uint256 savingsBalance; // Amount allocated to savings
        uint256 loanBalance; // Active loan balance
        bool isMember; // Membership status
    }

    mapping(address => Member) public members; // Mapping to store members' data
    address public owner; // Contract owner (admin)
    uint256 public totalShares; // Total shares issued
    uint256 public totalSavings; // Total savings in the group
    uint256 public totalLoans; // Total active loans
    uint256 public sharePrice = 1 ether; // Price per share (Can be set to cUSD for Celo)
    uint256 public savingsPercentage = 50; // Percentage of share purchase allocated to savings
    uint256 public loanLimitMultiplier = 2; // Loan limit = 2x shares held

    // Events for tracking contract activity
    event SharesPurchased(address indexed member, uint256 shares);
    event LoanRequested(address indexed member, uint256 amount);
    event LoanRepaid(address indexed member, uint256 amount);
    event SavingsAllocated(address indexed member, uint256 amount);

    // Modifier to restrict access to registered members only
    modifier onlyMember() {
        require(members[msg.sender].isMember, "Not a registered member");
        _;
    }

    // Constructor to initialize the contract
    constructor() {
        owner = msg.sender; // Set the deployer as the contract owner
    }

    /**
     * @dev Register a new member
     */
    function registerMember() external {
        require(!members[msg.sender].isMember, "Already a member");
        members[msg.sender] = Member(0, 0, 0, true); // Initialize member with zero shares, savings, and loans
    }

    /**
     * @dev Purchase shares and allocate a portion to savings
     * @param amount Number of shares to purchase
     */
    function purchaseShares(uint256 amount) external payable onlyMember {
        require(msg.value == amount * sharePrice, "Incorrect ETH sent");

        uint256 savingsAmount = (msg.value * savingsPercentage) / 100; // Calculate savings allocation
        uint256 remaining = msg.value - savingsAmount; // Remaining amount for shares

        // Update member details
        members[msg.sender].shares += amount;
        members[msg.sender].savingsBalance += savingsAmount;
        totalShares += amount;
        totalSavings += savingsAmount;

        emit SharesPurchased(msg.sender, amount);
        emit SavingsAllocated(msg.sender, savingsAmount);
    }

    /**
     * @dev Apply for a loan based on shares owned
     * @param amount Loan amount requested
     */
    function applyForLoan(uint256 amount) external onlyMember {
        uint256 maxLoan = members[msg.sender].shares * loanLimitMultiplier; // Max loan based on shares
        require(amount <= maxLoan, "Loan exceeds allowed limit");
        require(members[msg.sender].loanBalance == 0, "Existing loan must be repaid first");

        members[msg.sender].loanBalance = amount;
        totalLoans += amount;

        payable(msg.sender).transfer(amount); // Send loan amount to the borrower

        emit LoanRequested(msg.sender, amount);
    }

    /**
     * @dev Repay an active loan
     */
    function repayLoan() external payable onlyMember {
        require(members[msg.sender].loanBalance > 0, "No active loan");
        require(msg.value == members[msg.sender].loanBalance, "Incorrect repayment amount");

        totalLoans -= msg.value;
        members[msg.sender].loanBalance = 0;

        emit LoanRepaid(msg.sender, msg.value);
    }

    /**
     * @dev Set savings percentage (only contract owner can change it)
     * @param newPercentage New percentage for savings allocation
     */
    function setSavingsPercentage(uint256 newPercentage) external {
        require(msg.sender == owner, "Only owner can change settings");
        require(newPercentage <= 100, "Invalid percentage");
        savingsPercentage = newPercentage;
    }

    /**
     * @dev Withdraw savings balance
     * @param amount Amount to withdraw
     */
    function withdrawSavings(uint256 amount) external onlyMember {
        require(amount <= members[msg.sender].savingsBalance, "Insufficient savings");

        members[msg.sender].savingsBalance -= amount;
        totalSavings -= amount;
        payable(msg.sender).transfer(amount); // Transfer savings withdrawal to the member
    }

    /**
     * @dev Allow contract to receive ETH deposits
     */
    receive() external payable {}
}
