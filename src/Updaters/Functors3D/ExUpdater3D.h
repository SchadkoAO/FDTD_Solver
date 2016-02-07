/*
 * ExUpdater3D.h
 *
 *  Created on: 05 февр. 2016 г.
 *      Author: aleksandr
 */

#ifndef EXUPDATER3D_H_
#define EXUPDATER3D_H_

#include <thrust/device_vector.h>
#include <thrust/functional.h>

typedef thrust::device_ptr<float> d_ptr;

class ExUpdater3D {
public:
	__host__ __device__
	ExUpdater3D(d_ptr _Ex, d_ptr _Hy, d_ptr _Hz, d_ptr _epsilon, int _sizeX, int _sizeY, int _sizeZ, float _S )
														: Ex(_Ex), Hy(_Hy), Hz(_Hz),
														  epsilon(_epsilon), sizeX(_sizeX),
														  sizeY(_sizeY), sizeZ(_sizeZ), S(_S) {};

	__host__ __device__
	ExUpdater3D(): sizeX(0), sizeY(0), sizeZ(0), S(0) {}

	void setParams(d_ptr _Ex, d_ptr _Hy, d_ptr _Hz, d_ptr _epsilon, int _sizeX, int _sizeY, int _sizeZ, float _S) {
		Ex=_Ex;
		Hy=_Hy;
		Hz=_Hz;
		epsilon=_epsilon;
		sizeX=_sizeX;
		sizeY=_sizeY;
		sizeZ=_sizeZ;
		S=_S;
	}

	__host__ __device__
	~ExUpdater3D() {};

	__host__ __device__
	void operator() (const int indx);

	d_ptr Ex, Hy, Hz, epsilon;
	int sizeX, sizeY, sizeZ;
	float S;
};

#endif /* EXUPDATER3D_H_ */
