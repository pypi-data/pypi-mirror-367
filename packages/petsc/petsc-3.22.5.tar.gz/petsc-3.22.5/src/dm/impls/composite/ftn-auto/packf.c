#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* pack.c */
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

#include "petscdmcomposite.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcompositegetnumberdm_ DMCOMPOSITEGETNUMBERDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcompositegetnumberdm_ dmcompositegetnumberdm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcompositegetaccessarray_ DMCOMPOSITEGETACCESSARRAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcompositegetaccessarray_ dmcompositegetaccessarray
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcompositegetlocalaccessarray_ DMCOMPOSITEGETLOCALACCESSARRAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcompositegetlocalaccessarray_ dmcompositegetlocalaccessarray
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcompositerestoreaccessarray_ DMCOMPOSITERESTOREACCESSARRAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcompositerestoreaccessarray_ dmcompositerestoreaccessarray
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcompositerestorelocalaccessarray_ DMCOMPOSITERESTORELOCALACCESSARRAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcompositerestorelocalaccessarray_ dmcompositerestorelocalaccessarray
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcompositescatterarray_ DMCOMPOSITESCATTERARRAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcompositescatterarray_ dmcompositescatterarray
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcompositegatherarray_ DMCOMPOSITEGATHERARRAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcompositegatherarray_ dmcompositegatherarray
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcompositeadddm_ DMCOMPOSITEADDDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcompositeadddm_ dmcompositeadddm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcompositegetentriesarray_ DMCOMPOSITEGETENTRIESARRAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcompositegetentriesarray_ dmcompositegetentriesarray
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcompositecreate_ DMCOMPOSITECREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcompositecreate_ dmcompositecreate
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmcompositegetnumberdm_(DM dm,PetscInt *nDM, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(nDM);
*ierr = DMCompositeGetNumberDM(
	(DM)PetscToPointer((dm) ),nDM);
}
PETSC_EXTERN void  dmcompositegetaccessarray_(DM dm,Vec pvec,PetscInt *nwanted, PetscInt wanted[],Vec vecs[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(pvec);
CHKFORTRANNULLINTEGER(wanted);
PetscBool vecs_null = !*(void**) vecs ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vecs);
*ierr = DMCompositeGetAccessArray(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((pvec) ),*nwanted,wanted,vecs);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vecs_null && !*(void**) vecs) * (void **) vecs = (void *)-2;
}
PETSC_EXTERN void  dmcompositegetlocalaccessarray_(DM dm,Vec pvec,PetscInt *nwanted, PetscInt wanted[],Vec vecs[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(pvec);
CHKFORTRANNULLINTEGER(wanted);
PetscBool vecs_null = !*(void**) vecs ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vecs);
*ierr = DMCompositeGetLocalAccessArray(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((pvec) ),*nwanted,wanted,vecs);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vecs_null && !*(void**) vecs) * (void **) vecs = (void *)-2;
}
PETSC_EXTERN void  dmcompositerestoreaccessarray_(DM dm,Vec pvec,PetscInt *nwanted, PetscInt wanted[],Vec vecs[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(pvec);
CHKFORTRANNULLINTEGER(wanted);
PetscBool vecs_null = !*(void**) vecs ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vecs);
*ierr = DMCompositeRestoreAccessArray(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((pvec) ),*nwanted,wanted,vecs);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vecs_null && !*(void**) vecs) * (void **) vecs = (void *)-2;
}
PETSC_EXTERN void  dmcompositerestorelocalaccessarray_(DM dm,Vec pvec,PetscInt *nwanted, PetscInt wanted[],Vec *vecs, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(pvec);
CHKFORTRANNULLINTEGER(wanted);
PetscBool vecs_null = !*(void**) vecs ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vecs);
*ierr = DMCompositeRestoreLocalAccessArray(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((pvec) ),*nwanted,wanted,vecs);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vecs_null && !*(void**) vecs) * (void **) vecs = (void *)-2;
}
PETSC_EXTERN void  dmcompositescatterarray_(DM dm,Vec gvec,Vec *lvecs, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(gvec);
PetscBool lvecs_null = !*(void**) lvecs ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(lvecs);
*ierr = DMCompositeScatterArray(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((gvec) ),lvecs);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! lvecs_null && !*(void**) lvecs) * (void **) lvecs = (void *)-2;
}
PETSC_EXTERN void  dmcompositegatherarray_(DM dm,InsertMode *imode,Vec gvec,Vec *lvecs, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(gvec);
PetscBool lvecs_null = !*(void**) lvecs ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(lvecs);
*ierr = DMCompositeGatherArray(
	(DM)PetscToPointer((dm) ),*imode,
	(Vec)PetscToPointer((gvec) ),lvecs);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! lvecs_null && !*(void**) lvecs) * (void **) lvecs = (void *)-2;
}
PETSC_EXTERN void  dmcompositeadddm_(DM dmc,DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dmc);
CHKFORTRANNULLOBJECT(dm);
*ierr = DMCompositeAddDM(
	(DM)PetscToPointer((dmc) ),
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmcompositegetentriesarray_(DM dm,DM dms[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool dms_null = !*(void**) dms ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dms);
*ierr = DMCompositeGetEntriesArray(
	(DM)PetscToPointer((dm) ),dms);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dms_null && !*(void**) dms) * (void **) dms = (void *)-2;
}
PETSC_EXTERN void  dmcompositecreate_(MPI_Fint * comm,DM *packer, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(packer);
 PetscBool packer_null = !*(void**) packer ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(packer);
*ierr = DMCompositeCreate(
	MPI_Comm_f2c(*(comm)),packer);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! packer_null && !*(void**) packer) * (void **) packer = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
