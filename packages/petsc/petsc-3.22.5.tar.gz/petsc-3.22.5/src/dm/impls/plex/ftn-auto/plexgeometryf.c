#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* plexgeometry.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscdmplex.h"
#include "petscfe.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexfindvertices_ DMPLEXFINDVERTICES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexfindvertices_ dmplexfindvertices
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcomputeprojection2dto1d_ DMPLEXCOMPUTEPROJECTION2DTO1D
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcomputeprojection2dto1d_ dmplexcomputeprojection2dto1d
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcomputeprojection3dto1d_ DMPLEXCOMPUTEPROJECTION3DTO1D
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcomputeprojection3dto1d_ dmplexcomputeprojection3dto1d
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcomputeprojection3dto2d_ DMPLEXCOMPUTEPROJECTION3DTO2D
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcomputeprojection3dto2d_ dmplexcomputeprojection3dto2d
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcomputegeometryfvm_ DMPLEXCOMPUTEGEOMETRYFVM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcomputegeometryfvm_ dmplexcomputegeometryfvm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetminradius_ DMPLEXGETMINRADIUS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetminradius_ dmplexgetminradius
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsetminradius_ DMPLEXSETMINRADIUS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsetminradius_ dmplexsetminradius
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcomputegradientfvm_ DMPLEXCOMPUTEGRADIENTFVM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcomputegradientfvm_ dmplexcomputegradientfvm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetdatafvm_ DMPLEXGETDATAFVM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetdatafvm_ dmplexgetdatafvm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcoordinatestoreference_ DMPLEXCOORDINATESTOREFERENCE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcoordinatestoreference_ dmplexcoordinatestoreference
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexreferencetocoordinates_ DMPLEXREFERENCETOCOORDINATES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexreferencetocoordinates_ dmplexreferencetocoordinates
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsheargeometry_ DMPLEXSHEARGEOMETRY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsheargeometry_ dmplexsheargeometry
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmplexfindvertices_(DM dm,Vec coordinates,PetscReal *eps,IS *points, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(coordinates);
PetscBool points_null = !*(void**) points ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(points);
*ierr = DMPlexFindVertices(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((coordinates) ),*eps,points);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! points_null && !*(void**) points) * (void **) points = (void *)-2;
}
PETSC_EXTERN void  dmplexcomputeprojection2dto1d_(PetscScalar coords[],PetscReal R[], int *ierr)
{
CHKFORTRANNULLSCALAR(coords);
CHKFORTRANNULLREAL(R);
*ierr = DMPlexComputeProjection2Dto1D(coords,R);
}
PETSC_EXTERN void  dmplexcomputeprojection3dto1d_(PetscScalar coords[],PetscReal R[], int *ierr)
{
CHKFORTRANNULLSCALAR(coords);
CHKFORTRANNULLREAL(R);
*ierr = DMPlexComputeProjection3Dto1D(coords,R);
}
PETSC_EXTERN void  dmplexcomputeprojection3dto2d_(PetscInt *coordSize,PetscScalar coords[],PetscReal R[], int *ierr)
{
CHKFORTRANNULLSCALAR(coords);
CHKFORTRANNULLREAL(R);
*ierr = DMPlexComputeProjection3Dto2D(*coordSize,coords,R);
}
PETSC_EXTERN void  dmplexcomputegeometryfvm_(DM dm,Vec *cellgeom,Vec *facegeom, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool cellgeom_null = !*(void**) cellgeom ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(cellgeom);
PetscBool facegeom_null = !*(void**) facegeom ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(facegeom);
*ierr = DMPlexComputeGeometryFVM(
	(DM)PetscToPointer((dm) ),cellgeom,facegeom);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! cellgeom_null && !*(void**) cellgeom) * (void **) cellgeom = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! facegeom_null && !*(void**) facegeom) * (void **) facegeom = (void *)-2;
}
PETSC_EXTERN void  dmplexgetminradius_(DM dm,PetscReal *minradius, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLREAL(minradius);
*ierr = DMPlexGetMinRadius(
	(DM)PetscToPointer((dm) ),minradius);
}
PETSC_EXTERN void  dmplexsetminradius_(DM dm,PetscReal *minradius, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexSetMinRadius(
	(DM)PetscToPointer((dm) ),*minradius);
}
PETSC_EXTERN void  dmplexcomputegradientfvm_(DM dm,PetscFV fvm,Vec faceGeometry,Vec cellGeometry,DM *dmGrad, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(fvm);
CHKFORTRANNULLOBJECT(faceGeometry);
CHKFORTRANNULLOBJECT(cellGeometry);
PetscBool dmGrad_null = !*(void**) dmGrad ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dmGrad);
*ierr = DMPlexComputeGradientFVM(
	(DM)PetscToPointer((dm) ),
	(PetscFV)PetscToPointer((fvm) ),
	(Vec)PetscToPointer((faceGeometry) ),
	(Vec)PetscToPointer((cellGeometry) ),dmGrad);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dmGrad_null && !*(void**) dmGrad) * (void **) dmGrad = (void *)-2;
}
PETSC_EXTERN void  dmplexgetdatafvm_(DM dm,PetscFV fv,Vec *cellgeom,Vec *facegeom,DM *gradDM, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(fv);
PetscBool cellgeom_null = !*(void**) cellgeom ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(cellgeom);
PetscBool facegeom_null = !*(void**) facegeom ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(facegeom);
PetscBool gradDM_null = !*(void**) gradDM ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(gradDM);
*ierr = DMPlexGetDataFVM(
	(DM)PetscToPointer((dm) ),
	(PetscFV)PetscToPointer((fv) ),cellgeom,facegeom,gradDM);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! cellgeom_null && !*(void**) cellgeom) * (void **) cellgeom = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! facegeom_null && !*(void**) facegeom) * (void **) facegeom = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! gradDM_null && !*(void**) gradDM) * (void **) gradDM = (void *)-2;
}
PETSC_EXTERN void  dmplexcoordinatestoreference_(DM dm,PetscInt *cell,PetscInt *numPoints, PetscReal realCoords[],PetscReal refCoords[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLREAL(realCoords);
CHKFORTRANNULLREAL(refCoords);
*ierr = DMPlexCoordinatesToReference(
	(DM)PetscToPointer((dm) ),*cell,*numPoints,realCoords,refCoords);
}
PETSC_EXTERN void  dmplexreferencetocoordinates_(DM dm,PetscInt *cell,PetscInt *numPoints, PetscReal refCoords[],PetscReal realCoords[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLREAL(refCoords);
CHKFORTRANNULLREAL(realCoords);
*ierr = DMPlexReferenceToCoordinates(
	(DM)PetscToPointer((dm) ),*cell,*numPoints,refCoords,realCoords);
}
PETSC_EXTERN void  dmplexsheargeometry_(DM dm,DMDirection *direction,PetscReal multipliers[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLREAL(multipliers);
*ierr = DMPlexShearGeometry(
	(DM)PetscToPointer((dm) ),*direction,multipliers);
}
#if defined(__cplusplus)
}
#endif
