#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* vscat.c */
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

#include "petscsf.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecscattersetup_ VECSCATTERSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecscattersetup_ vecscattersetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecscattersettype_ VECSCATTERSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecscattersettype_ vecscattersettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecscattergettype_ VECSCATTERGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecscattergettype_ vecscattergettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecscattergetmerged_ VECSCATTERGETMERGED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecscattergetmerged_ vecscattergetmerged
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecscatterdestroy_ VECSCATTERDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecscatterdestroy_ vecscatterdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecscattercopy_ VECSCATTERCOPY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecscattercopy_ vecscattercopy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecscatterviewfromoptions_ VECSCATTERVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecscatterviewfromoptions_ vecscatterviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecscatterview_ VECSCATTERVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecscatterview_ vecscatterview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecscatterremap_ VECSCATTERREMAP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecscatterremap_ vecscatterremap
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecscattersetfromoptions_ VECSCATTERSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecscattersetfromoptions_ vecscattersetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecscattercreate_ VECSCATTERCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecscattercreate_ vecscattercreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecscattercreatetoall_ VECSCATTERCREATETOALL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecscattercreatetoall_ vecscattercreatetoall
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecscattercreatetozero_ VECSCATTERCREATETOZERO
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecscattercreatetozero_ vecscattercreatetozero
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecscatterbegin_ VECSCATTERBEGIN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecscatterbegin_ vecscatterbegin
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecscatterend_ VECSCATTEREND
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecscatterend_ vecscatterend
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  vecscattersetup_(VecScatter *sf, int *ierr)
{
*ierr = VecScatterSetUp(*sf);
}
PETSC_EXTERN void  vecscattersettype_(VecScatter *sf,VecScatterType *type, int *ierr)
{
*ierr = VecScatterSetType(*sf,*type);
}
PETSC_EXTERN void  vecscattergettype_(VecScatter *sf,VecScatterType *type, int *ierr)
{
*ierr = VecScatterGetType(*sf,type);
}
PETSC_EXTERN void  vecscattergetmerged_(VecScatter *sf,PetscBool *flg, int *ierr)
{
*ierr = VecScatterGetMerged(*sf,flg);
}
PETSC_EXTERN void  vecscatterdestroy_(VecScatter *sf, int *ierr)
{
*ierr = VecScatterDestroy(sf);
}
PETSC_EXTERN void  vecscattercopy_(VecScatter *sf,VecScatter *newsf, int *ierr)
{
*ierr = VecScatterCopy(*sf,newsf);
}
PETSC_EXTERN void  vecscatterviewfromoptions_(VecScatter *sf,PetscObject obj, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = VecScatterViewFromOptions(*sf,
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  vecscatterview_(VecScatter *sf,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = VecScatterView(*sf,PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  vecscatterremap_(VecScatter *sf,PetscInt tomap[],PetscInt frommap[], int *ierr)
{
CHKFORTRANNULLINTEGER(tomap);
CHKFORTRANNULLINTEGER(frommap);
*ierr = VecScatterRemap(*sf,tomap,frommap);
}
PETSC_EXTERN void  vecscattersetfromoptions_(VecScatter *sf, int *ierr)
{
*ierr = VecScatterSetFromOptions(*sf);
}
PETSC_EXTERN void  vecscattercreate_(Vec x,IS ix,Vec y,IS iy,VecScatter *newsf, int *ierr)
{
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(ix);
CHKFORTRANNULLOBJECT(y);
CHKFORTRANNULLOBJECT(iy);
*ierr = VecScatterCreate(
	(Vec)PetscToPointer((x) ),
	(IS)PetscToPointer((ix) ),
	(Vec)PetscToPointer((y) ),
	(IS)PetscToPointer((iy) ),newsf);
}
PETSC_EXTERN void  vecscattercreatetoall_(Vec vin,VecScatter *ctx,Vec *vout, int *ierr)
{
CHKFORTRANNULLOBJECT(vin);
PetscBool vout_null = !*(void**) vout ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vout);
*ierr = VecScatterCreateToAll(
	(Vec)PetscToPointer((vin) ),ctx,vout);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vout_null && !*(void**) vout) * (void **) vout = (void *)-2;
}
PETSC_EXTERN void  vecscattercreatetozero_(Vec vin,VecScatter *ctx,Vec *vout, int *ierr)
{
CHKFORTRANNULLOBJECT(vin);
PetscBool vout_null = !*(void**) vout ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vout);
*ierr = VecScatterCreateToZero(
	(Vec)PetscToPointer((vin) ),ctx,vout);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vout_null && !*(void**) vout) * (void **) vout = (void *)-2;
}
PETSC_EXTERN void  vecscatterbegin_(VecScatter *sf,Vec x,Vec y,InsertMode *addv,ScatterMode *mode, int *ierr)
{
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(y);
*ierr = VecScatterBegin(*sf,
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((y) ),*addv,*mode);
}
PETSC_EXTERN void  vecscatterend_(VecScatter *sf,Vec x,Vec y,InsertMode *addv,ScatterMode *mode, int *ierr)
{
CHKFORTRANNULLOBJECT(x);
CHKFORTRANNULLOBJECT(y);
*ierr = VecScatterEnd(*sf,
	(Vec)PetscToPointer((x) ),
	(Vec)PetscToPointer((y) ),*addv,*mode);
}
#if defined(__cplusplus)
}
#endif
