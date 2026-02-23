// MongoURI.cpp
// author: Johannes Wagner <wagner@hcm-lab.de>, Tobias Hallmen
// created: 2016/10/19
// Copyright (C) 2007-26 University of Augsburg, Chair for Human-Centered Artificial Intelligence
//
// *************************************************************************************************
//
// This file is part of Social Signal Interpretation (SSI) developed at the 
// Chair for Human-Centered Artificial Intelligence of the University of Augsburg
//
// This library is free software; you can redistribute itand/or
// modify it under the terms of the GNU General Public
// License as published by the Free Software Foundation; either
// version 3 of the License, or any laterversion.
//
// This library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FORA PARTICULAR PURPOSE.  See the GNU
// General Public License for more details.
//
// You should have received a copy of the GNU General Public
// License along withthis library; if not, write to the Free Software
// Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
//

#include "MongoURI.h"
#include "base/String.h"

#include <mongoc/mongoc.h>
#include <iomanip>
#include <sstream>
#include <cctype>

static std::string url_encode(const std::string &value) {
	std::ostringstream escaped;
	escaped.fill('0');
	escaped << std::hex;

	for (std::string::const_iterator i = value.begin(), n = value.end(); i != n; ++i) {
		std::string::value_type c = (*i);

		// Keep alphanumeric and other safe characters
		if (isalnum((unsigned char)c) || c == '-' || c == '_' || c == '.' || c == '~') {
			escaped << c;
			continue;
		}

		// Any other characters are percent-encoded
		escaped << std::uppercase;
		escaped << '%' << std::setw(2) << int((unsigned char)c);
		escaped << std::nouppercase;
	}

	return escaped.str();
}

namespace ssi
{
	ssi_char_t *MongoURI::ssi_log_name = "mongouri__";

	MongoURI::MongoURI(const ssi_char_t *ip, ssi_size_t port, const ssi_char_t *username, const ssi_char_t *password)
	{
		ssi_char_t address[SSI_MAX_CHAR];
		ssi_sprint(address, "%s:%u", ip, port);

		_address = ssi_strcpy(address);

		std::string encoded_user = url_encode(username ? username : "");
		std::string encoded_pass = url_encode(password ? password : "");

		ssi_char_t uri[SSI_MAX_CHAR];
		ssi_sprint(uri, "mongodb://%s:%s@%s", encoded_user.c_str(), encoded_pass.c_str(), address);

		_uri = ssi_strcpy(uri);		
	}
	
	MongoURI::~MongoURI()
	{
		delete[] _address; _address = 0;
		delete[] _uri; _uri = 0;
	}

	const ssi_char_t *MongoURI::getURI()
	{
		return _uri;
	}

	const ssi_char_t *MongoURI::getAddress()
	{
		return _address;
	}

}