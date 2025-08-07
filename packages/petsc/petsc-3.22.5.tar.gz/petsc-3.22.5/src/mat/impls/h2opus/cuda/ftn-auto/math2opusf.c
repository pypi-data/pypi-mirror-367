#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* math2opus.cu */
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

#include "petscmat.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define math2opusorthogonalize_ MATH2OPUSORTHOGONALIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define math2opusorthogonalize_ math2opusorthogonalize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define math2opuscompress_ MATH2OPUSCOMPRESS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define math2opuscompress_ math2opuscompress
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define math2opussetsamplingmat_ MATH2OPUSSETSAMPLINGMAT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define math2opussetsamplingmat_ math2opussetsamplingmat
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreateh2opusfrommat_ MATCREATEH2OPUSFROMMAT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreateh2opusfrommat_ matcreateh2opusfrommat
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define math2opusgetindexmap_ MATH2OPUSGETINDEXMAP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define math2opusgetindexmap_ math2opusgetindexmap
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define math2opusmapvec_ MATH2OPUSMAPVEC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define math2opusmapvec_ math2opusmapvec
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define math2opuslowrankupdate_ MATH2OPUSLOWRANKUPDATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define math2opuslowrankupdate_ math2opuslowrankupdate
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  math2opusorthogonalize_(Mat A, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatH2OpusOrthogonalize(
	(Mat)PetscToPointer((A) ));
}
PETSC_EXTERN void  math2opuscompress_(Mat A,PetscReal *tol, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatH2OpusCompress(
	(Mat)PetscToPointer((A) ),*tol);
}
PETSC_EXTERN void  math2opussetsamplingmat_(Mat A,Mat B,PetscInt *bs,PetscReal *tol, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(B);
*ierr = MatH2OpusSetSamplingMat(
	(Mat)PetscToPointer((A) ),
	(Mat)PetscToPointer((B) ),*bs,*tol);
}
PETSC_EXTERN void  matcreateh2opusfrommat_(Mat B,PetscInt *spacedim, PetscReal coords[],PetscBool *cdist,PetscReal *eta,PetscInt *leafsize,PetscInt *maxrank,PetscInt *bs,PetscReal *rtol,Mat *nA, int *ierr)
{
CHKFORTRANNULLOBJECT(B);
CHKFORTRANNULLREAL(coords);
PetscBool nA_null = !*(void**) nA ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(nA);
*ierr = MatCreateH2OpusFromMat(
	(Mat)PetscToPointer((B) ),*spacedim,coords,*cdist,*eta,*leafsize,*maxrank,*bs,*rtol,nA);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! nA_null && !*(void**) nA) * (void **) nA = (void *)-2;
}
PETSC_EXTERN void  math2opusgetindexmap_(Mat A,IS *indexmap, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool indexmap_null = !*(void**) indexmap ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(indexmap);
*ierr = MatH2OpusGetIndexMap(
	(Mat)PetscToPointer((A) ),indexmap);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! indexmap_null && !*(void**) indexmap) * (void **) indexmap = (void *)-2;
}
PETSC_EXTERN void  math2opusmapvec_(Mat A,PetscBool *nativetopetsc,Vec in,Vec *out, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(in);
PetscBool out_null = !*(void**) out ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(out);
*ierr = MatH2OpusMapVec(
	(Mat)PetscToPointer((A) ),*nativetopetsc,
	(Vec)PetscToPointer((in) ),out);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! out_null && !*(void**) out) * (void **) out = (void *)-2;
}
PETSC_EXTERN void  math2opuslowrankupdate_(Mat A,Mat U,Mat V,PetscScalar *s, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(U);
CHKFORTRANNULLOBJECT(V);
*ierr = MatH2OpusLowRankUpdate(
	(Mat)PetscToPointer((A) ),
	(Mat)PetscToPointer((U) ),
	(Mat)PetscToPointer((V) ),*s);
}
#if defined(__cplusplus)
}
#endif
