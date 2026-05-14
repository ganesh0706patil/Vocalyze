import { uploadVideo } from "./videoService";
import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const saveAssessment = async (assessmentData, onProgressUpdate) => {
  const videoUrls = assessmentData.feedback
    .map((f) => f?.videoUrl)
    .filter(Boolean);

  if (videoUrls.length === 0) {
    throw new Error("No videos found to upload");
  }

  const uploadedUrls = [];
  const currUser = JSON.parse(localStorage.getItem("currUser"));
  
  for (let i = 0; i < videoUrls.length; i++) {
    const s3Data = await uploadVideo(videoUrls[i], i);
    uploadedUrls.push(s3Data.url);
    onProgressUpdate(((i + 1) / videoUrls.length) * 100);
  }

  const updatedFeedback = assessmentData.feedback.map((feedback, index) => ({
    ...feedback,
    videoUrl: uploadedUrls[index] || feedback.videoUrl 
  }));

  const updatedAssessmentData = {
    ...assessmentData,
    feedback: updatedFeedback
  };

  // Stringify data for backend storage compatibility
  const response = await axios.post(
    `${API_BASE_URL}/assessments/save`,
    {
      assessmentData: updatedAssessmentData, 
    },
    {
      headers: {
        "x-user-email": currUser.email,
        "Content-Type": "application/json"
      },
    }
  );

  return response.data;
};

export const deleteAssessment = async (assessmentId) => {
  try {
    const response = await axios.delete(
      `${API_BASE_URL}/assessments/${assessmentId}`,
      {
        headers: {
          "x-user-email": JSON.parse(localStorage.getItem("currUser"))?.email,
        },
      }
    );

    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || error.message);
  }
};

export const getAssessment = async (assessmentId) => {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/assessments/${assessmentId}`,
      {
        headers: {
          "x-user-email": JSON.parse(localStorage.getItem("currUser"))?.email,
        },
      }
    );

    const { id, data, dateAndTime, createdAt, updatedAt } = response.data.assessment;

    // Handle backend data format which stores complex objects as JSON strings
    let parsedData;
    try {
      parsedData = typeof data === 'string' ? JSON.parse(data) : data;
    } catch (parseError) {
      console.error('Error parsing assessment data:', parseError);
      throw new Error('Failed to parse assessment data');
    }

    return {
      id,
      data: parsedData,
      dateAndTime,
      createdAt,
      updatedAt,
    };
  } catch (error) {
    console.error('Error fetching assessment:', error);
    throw new Error(error.response?.data?.error || error.message);
  }
};

export const getAllAssessments = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/assessments/all`, {
      headers: {
        "x-user-email": JSON.parse(localStorage.getItem("currUser"))?.email,
      },
    });

    return response.data.assessments.map((assessment) => {
      let parsedData = assessment.data;

      // Defensive Parsing: Peels back layers of stringification if they exist
      try {
        while (typeof parsedData === 'string') {
          parsedData = JSON.parse(parsedData);
        }
      } catch (e) {
        console.error("Failed to parse data for assessment:", assessment.id, e);
        parsedData = {}; // Fallback to avoid breaking the UI
      }

      return {
        id: assessment._id || assessment.id,
        data: parsedData, // Now guaranteed to be an Object
        dateAndTime: assessment.dateAndTime,
        createdAt: assessment.createdAt,
        updatedAt: assessment.updatedAt,
      };
    });
  } catch (error) {
    console.error('Error fetching assessments:', error);
    throw new Error(error.response?.data?.error || error.message);
  }
};