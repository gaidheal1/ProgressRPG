import axios from './axios';

export const loginUser = async (username, password) => {
	const response = await axios.post('/auth/jwt/create/', {
		username,
		password,
	});
	return response.data;
};
