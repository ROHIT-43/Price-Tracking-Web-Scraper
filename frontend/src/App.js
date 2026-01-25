import React, { useState, useEffect } from "react";
import SearchTextList from "./components/SearchTextList";
import PriceHistoryTable from "./components/PriceHistoryTable";
import axios from "axios";
import TrackedProductList from "./components/TrackedProductList";

const URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function App() {
  const [showPriceHistory, setShowPriceHistory] = useState(false);
  const [priceHistory, setPriceHistory] = useState([]);
  const [searchTexts, setSearchTexts] = useState([]);
  const [newSearchText, setNewSearchText] = useState("");

  useEffect(() => {
    fetchUniqueSearchTexts();
    
    // Refresh search texts list every 30 seconds to pick up new searches
    const refreshInterval = setInterval(() => {
      fetchUniqueSearchTexts();
    }, 30000);
    
    return () => clearInterval(refreshInterval);
  }, []);

  const fetchUniqueSearchTexts = async () => {
    try {
      const response = await axios.get(`${URL}/unique_search_texts`);
      const data = response.data;
      setSearchTexts(data);
    } catch (error) {
      console.error("Error fetching unique search texts:", error);
    }
  };

  const handleSearchTextClick = async (searchText) => {
    try {
      const response = await axios.get(
        `${URL}/results?search_text=${searchText}`
      );

      const data = response.data;
      setPriceHistory(data);
      setShowPriceHistory(true);
    } catch (error) {
      console.error("Error fetching price history:", error);
    }
  };

  const handlePriceHistoryClose = () => {
    setShowPriceHistory(false);
    setPriceHistory([]);
  };

  const handleNewSearchTextChange = (event) => {
    setNewSearchText(event.target.value);
  };

  const handleNewSearchTextSubmit = async (event) => {
    event.preventDefault();
    const searchTextToSubmit = newSearchText;

    try {
      await axios.post(`${URL}/start-scraper`, {
        search_text: searchTextToSubmit,
        url: "https://amazon.ca",
      });

      alert("Scraper started successfully! Results will appear in a few minutes.");
      setSearchTexts([...searchTexts, searchTextToSubmit]);
      setNewSearchText("");
      
      // Poll for results - check every 5 seconds for up to 3 minutes (36 times)
      let attempts = 0;
      const maxAttempts = 36; // 3 minutes total
      const pollInterval = setInterval(async () => {
        attempts++;
        try {
          const response = await axios.get(
            `${URL}/results?search_text=${encodeURIComponent(searchTextToSubmit)}`
          );
          
          if (response.data && response.data.length > 0) {
            // Results are ready! Display them
            setPriceHistory(response.data);
            setShowPriceHistory(true);
            clearInterval(pollInterval);
            // Refresh the search texts list to ensure it's up to date
            fetchUniqueSearchTexts();
          } else if (attempts >= maxAttempts) {
            // Stop polling after max attempts
            clearInterval(pollInterval);
            alert("Scraper is taking longer than expected. Please check back later or refresh the page.");
          }
        } catch (error) {
          // Continue polling even if there's an error
          if (attempts >= maxAttempts) {
            clearInterval(pollInterval);
          }
        }
      }, 5000); // Check every 5 seconds
      
    } catch (error) {
      alert("Error starting scraper: " + error.message);
    }
  };

  return (
    <div className="main">
      <h1>Product Search Tool</h1>
      <form onSubmit={handleNewSearchTextSubmit}>
        <label>Search for a new item:</label>
        <input
          type="text"
          value={newSearchText}
          onChange={handleNewSearchTextChange}
        />
        <button type="submit">Start Scraper</button>
      </form>
      <SearchTextList
        searchTexts={searchTexts}
        onSearchTextClick={handleSearchTextClick}
      />
      <TrackedProductList />
      {showPriceHistory && (
        <PriceHistoryTable
          priceHistory={priceHistory}
          onClose={handlePriceHistoryClose}
        />
      )}
    </div>
  );
}

export default App;
