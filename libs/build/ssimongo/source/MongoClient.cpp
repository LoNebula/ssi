// MongoClient.cpp
// author: Johannes Wagner <wagner@hcm-lab.de>, Tobias Hallmen
// created: 2016/10/19
// Copyright (C) 2007-26 University of Augsburg, Lab for Human Centered Multimedia
//
// *************************************************************************************************
//
// This file is part of Social Signal Interpretation (SSI) developed at the 
// Lab for Human Centered Multimedia of the University of Augsburg
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

#include "MongoClient.h"
#include "MongoDB.h"
#include "MongoURI.h"

#include <mongoc/mongoc.h>

namespace ssi
{
	ssi_char_t *MongoClient::ssi_log_name = "mongoclnt_";

	MongoClient::MongoClient()
	: _name(0),
		_db_name(0),
		_client(0),
		_uri(0),
		_db(0)
	{
		static MongoDB db;
	}

	MongoClient::~MongoClient()
	{
		close();
	}

	bool MongoClient::check()
	{
		if (!_uri || !_client || !_db)
		{
			return false;
		}

		mongoc_read_prefs_t *prefs = mongoc_read_prefs_new(MONGOC_READ_PRIMARY);
		bson_t reply;
		bson_error_t error;

		bson_t *cmd = BCON_NEW("ping", BCON_INT32(1));
		bool result = mongoc_client_command_simple(_client, "admin", cmd, NULL, &reply, &error);
		bson_destroy(cmd);
		
		if (!result)
		{
			ssi_wrn("check failed '%s' (domain=%u, code=%u)", error.message, error.domain, error.code);
		}
		
		mongoc_read_prefs_destroy(prefs);

		return result;
	}

	bool MongoClient::connect(MongoURI &uri, const ssi_char_t *db_name, bool auto_create, ssi_size_t timeout, bool tls, bool verify)
	{
		bson_error_t error;

		if (_client)
		{
			ssi_wrn("already connected '%s'", _name);
			return false;
		}

		_name = ssi_strcat(db_name, "@", uri.getAddress());
		_db_name = ssi_strcpy(db_name);

		ssi_msg(SSI_LOG_LEVEL_BASIC, "connect (name='%s', timeout=%u, tls=%s, verify=%s)", _name, timeout, tls ? "true" : "false", verify ? "true" : "false");

		ssi_char_t tmp[SSI_MAX_CHAR];
		ssi_size_t timeout_val = (timeout > 0) ? timeout : 10000;
		sprintf(tmp, "%s/%s?connectTimeoutMS=%u&socketTimeoutMS=%u&serverSelectionTimeoutMS=%u", uri.getURI(), db_name, timeout_val, timeout_val, timeout_val);

		if (tls) {
			strcat(tmp, "&tls=true");
			if (!verify) {
				strcat(tmp, "&tlsInsecure=true");
			}
		}

		strcat(tmp, "&authSource=admin");

		// strcat(tmp, "&directConnection=true");
		// strcat(tmp, "&authSource=admin");

		ssi_print("\n[mongoclnt_] uri='%s'\n", tmp);

		_uri = mongoc_uri_new(tmp);
			
		if (!_uri)
		{
			ssi_wrn("could not create uir");
			return false;
		}
		_client = mongoc_client_new_from_uri(_uri);
		if (!_client)
		{
			ssi_wrn("could not create client");
			return false;
		}

		mongoc_client_set_error_api(_client, MONGOC_ERROR_API_VERSION_2);

		_db = mongoc_client_get_database(_client, _db_name);
		if (!_db)
		{
			ssi_wrn("could not connect database '%s'", _name);
			return false;
		}

		ssi_print("[mongoclnt_] starting check...\n");
		long long t0 = GetTickCount64();
		if (!check())
		{
			long long t1 = GetTickCount64();
			ssi_print("[mongoclnt_] check finished in %lld ms\n", t1 - t0);
			ssi_wrn("could not connect '%s'", _name);
			close();
			return false;
		}
		ssi_print("[mongoclnt_] check success in %lld ms\n", GetTickCount64() - t0);

		return true;
	}

	bool MongoClient::is_connected()
	{
		return _uri && _client && _db;
	}

	const ssi_char_t *MongoClient::getName()
	{
		return _name;
	}

	void MongoClient::close()
	{
		if (is_connected())
		{

			ssi_msg(SSI_LOG_LEVEL_BASIC, "close '%s'", _name);

			if (_client)
			{
				mongoc_uri_destroy(_uri); _uri = 0;
			}
			if (_client)
			{
				mongoc_client_destroy(_client); _client = 0;
			}
			if (_db)
			{
				mongoc_database_destroy(_db); _db = 0;
			}
		}

		delete[] _name; _name = 0;
		delete[] _db_name; _db_name = 0;
	}

	bool MongoClient::has(MongoCollection &collection)
	{
		if (!is_connected())
		{
			ssi_wrn("client not connected");
			return false;
		}

		return mongoc_database_has_collection(_db, collection.getName(), NULL);
	}

	bool MongoClient::get(MongoCollection &collection)
	{
		if (!is_connected())
		{
			ssi_wrn("client not connected");
			return false;
		}

		mongoc_collection_t *c = 0;

		if (has(collection))
		{		
			c = mongoc_database_get_collection(_db, collection.getName());
		}

		if (!c)
		{
			ssi_wrn("could not get collection '%s'", collection.getName());
			return false;
		}

		collection.set(c);

		return true;
	}

	bool MongoClient::add(MongoCollection &collection)
	{
		if (!is_connected())
		{
			ssi_wrn("client not connected");
			return false;
		}

		mongoc_collection_t *c = 0;

		if (!has(collection))
		{
			c = mongoc_database_create_collection(_db, collection.getName(), NULL, NULL);
		}
		else
		{
			c = mongoc_database_get_collection(_db, collection.getName());
		}

		if (!c)
		{
			ssi_wrn("could not get collection '%s'", collection.getName());
			return false;
		}

		collection.set(c);

		return true;
	}
}