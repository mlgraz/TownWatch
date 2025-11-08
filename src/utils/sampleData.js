/**
 * Sample data for testing the TownWatch application
 */

export const sampleDocuments = [
  {
    title: 'City Council Meeting - Budget Discussion',
    content: 'The City Council convened to discuss the proposed budget for the upcoming fiscal year. Major topics included infrastructure improvements, public safety funding, and education initiatives. Council members debated the allocation of $2.5 million for road repairs and the creation of new bike lanes throughout the downtown area. There was strong support for increasing funding to local schools, with several members advocating for enhanced STEM programs.',
    date: '2024-10-15',
    source: 'City Council',
    jurisdiction: 'San Francisco, CA',
    topics: ['Budget', 'Infrastructure', 'Education'],
    url: 'https://example.gov/meetings/2024-10-15',
  },
  {
    title: 'Planning Commission - Zoning Variance Request',
    content: 'The Planning Commission reviewed a zoning variance request for a proposed mixed-use development at 123 Main Street. The developer is seeking approval to build a 5-story building that would include retail space on the ground floor and residential units above. Community members expressed concerns about parking availability and potential traffic impacts. The commission voted to table the decision pending additional traffic studies.',
    date: '2024-10-20',
    source: 'Planning Commission',
    jurisdiction: 'San Francisco, CA',
    topics: ['Zoning', 'Housing', 'Development'],
    url: 'https://example.gov/planning/2024-10-20',
  },
  {
    title: 'Board of Supervisors - Climate Action Plan',
    content: 'The Board of Supervisors approved an ambitious climate action plan aimed at achieving carbon neutrality by 2035. The plan includes measures to expand renewable energy sources, improve public transportation, and retrofit existing buildings for energy efficiency. Supervisor Johnson emphasized the importance of green jobs creation as part of the transition. The plan allocates $10 million for initial implementation over the next two years.',
    date: '2024-11-01',
    source: 'Board of Supervisors',
    jurisdiction: 'San Francisco, CA',
    topics: ['Climate', 'Environment', 'Sustainability'],
    url: 'https://example.gov/supervisors/2024-11-01',
  },
  {
    title: 'City Council - Affordable Housing Initiative',
    content: 'City Council members unanimously approved a new affordable housing initiative designed to address the growing housing crisis. The initiative includes tax incentives for developers who include affordable units in their projects, as well as direct funding for the construction of 500 new affordable housing units over the next three years. Council Member Martinez highlighted that the program will prioritize housing for low-income families, seniors, and individuals experiencing homelessness.',
    date: '2024-10-25',
    source: 'City Council',
    jurisdiction: 'Oakland, CA',
    topics: ['Housing', 'Affordable Housing', 'Development'],
  },
  {
    title: 'Public Safety Committee - Police Reform Proposals',
    content: 'The Public Safety Committee held a special session to discuss proposed police reform measures. Key proposals include the establishment of a civilian oversight board, enhanced training requirements for officers, and the implementation of body-worn cameras for all patrol officers. Community advocates presented testimony supporting the reforms, while the police union raised concerns about certain provisions. The committee agreed to schedule additional hearings before making recommendations to the full council.',
    date: '2024-11-03',
    source: 'Public Safety Committee',
    jurisdiction: 'Oakland, CA',
    topics: ['Public Safety', 'Police Reform', 'Community'],
  },
  {
    title: 'Parks and Recreation - Community Center Expansion',
    content: 'The Parks and Recreation Department presented plans for expanding the downtown community center. The $3 million project would add a new gymnasium, multipurpose rooms, and a senior activity center. The expansion is designed to serve the growing population in the downtown area and provide additional programming space for youth sports, arts classes, and senior services. Public input sessions are scheduled for next month.',
    date: '2024-10-18',
    source: 'Parks and Recreation',
    jurisdiction: 'San Francisco, CA',
    topics: ['Parks', 'Recreation', 'Community Services'],
  },
];

/**
 * Helper function to add sample data to storage
 */
export const loadSampleData = async (storageService) => {
  try {
    for (const docData of sampleDocuments) {
      await storageService.addDocument(docData);
    }
    return true;
  } catch (error) {
    console.error('Error loading sample data:', error);
    return false;
  }
};
