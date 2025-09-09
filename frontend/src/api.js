import axios from "axios";

export async function callApi(accessToken) {
  try {
    const response = await axios.get(
      `${process.env.REACT_APP_API_BASE_URL}/auth/me`,
      {
        headers: {
          Authorization: `Bearer ${accessToken}`
        }
      }
    );
    return response.data;
  } catch (err) {
    console.error(err);
    throw err;
  }
}
