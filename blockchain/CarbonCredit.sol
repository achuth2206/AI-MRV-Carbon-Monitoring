// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CarbonCredit {

    struct Project {
        uint256 id;
        string projectId;
        uint256 area;
        uint256 carbonCredits;
        uint256 estimatedValue;
        string classification;
        uint256 confidenceScore;
        uint256 timestamp;
    }

    Project[] public projects;

    event ProjectAdded(uint256 id, string projectId);

    function addProject(
        string memory _projectId,
        uint256 _area,
        uint256 _carbonCredits,
        uint256 _estimatedValue,
        string memory _classification,
        uint256 _confidenceScore
    ) public {

        projects.push(Project(
            projects.length,
            _projectId,
            _area,
            _carbonCredits,
            _estimatedValue,
            _classification,
            _confidenceScore,
            block.timestamp
        ));

        emit ProjectAdded(projects.length - 1, _projectId);
    }

    function getProject(uint256 _id) public view returns (Project memory) {
        return projects[_id];
    }

    function getTotalProjects() public view returns (uint256) {
        return projects.length;
    }
}